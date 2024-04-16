from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import CharacterTextSplitter

from app.config.config import settings


def summary_script(file):
    # 문서요약하기
    with open(file, "r",
              encoding="utf-8") as f:
        read_text = f.read()

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=4000, chunk_overlap=150, separator='}'
    )

    docs = [Document(page_content=x) for x in text_splitter.split_text(read_text)]
    split_docs = text_splitter.split_documents(docs)

    # print(docs)
    # for doc in docs:
    #     print(doc)
    #
    # print("sprit_docs")
    # print(split_docs)
    # for doc in split_docs:
    #     print(doc)
    #
    # return

    # Map 프롬프트
    map_template = """다음은 여러 개의 문서입니다.
        {docs}
        당신은 주어진 문서에서 주요 주제를 추출하는 데 도움이 되는 전문 기자입니다.
        이 문서 목록을 기반으로 주요 주제를 식별해 주세요.
        주요 주제에는 해당 타임스탬프도 같이 포함해 주세요.
        타임스탬프 형식은 (시작: 0.123, 끝: 130.643) 입니다.
        주제 하나마다 주요 정치관련 키워드도 세개 식별해주세요.
        차근차근 단계적으로 생각해주세요.

        형식:
        1. 주제 (키워드: 키워드 1, 키워드 2, 키워드 3)
         - 주제에 대한 설명입니다.
        ...

        예시:
        1. 강북을 중심으로 한 민주당 공천 논란 (키워드: 박영진 의원, 강북 공천, 한민수 후보)
         - 조국신당을 중심으로 한 정권심판론과 정책 대결이 치열하게 전개되고 있으며, 이는 선거 전략에 영향을 미칠 것으로 보인다. (시작: 973.268, 끝: 1049.48)

        주의:
        주제를 10개 이상 나열하지 마십시오.
        주제의 길이가 300초를 초과하지 않도록 주의하십시오.

        도움이 되는 답변:"""

    # + 주요 테마에 대해서 예시 추가하기.
    map_prompt = PromptTemplate.from_template(map_template)

    # Reduce 프롬프트
    reduce_template = """다음은 여러 개의 요약입니다:
        {doc_summaries}
        당신은 요약 작성에 능숙한 전문가입니다.
        번호가 매겨진 요약 목록이 주어졌습니다.
        요약 목록에서 상위 3가지 중요한 통찰을 추출한 후에, 해당 통찰의 요약을 작성하겠습니다.
        주요 테마에는 타임스탬프도 같이 포함해 주세요.
        타임스탬프 형식은 (시작: 0.123, 끝: 130.643) 입니다.
        단락 하나마다 주요 정치관련 키워드도 세개 식별해주세요.
        키워드는 제목에 포함된 단어가 들어가지 않아야합니다.
        키워드 형식은 (키워드:박영진 의원, 강북 공천, 한민수 후보) 입니다.
        차근차근 단계적으로 생각해주세요.

        형식:
        1. 주제 (키워드: 키워드 1, 키워드 2, 키워드 3)
         - 주제에 대한 설명입니다.
        ...

        예시:
        1. 당정 갈등 및 화해 (키워드: 윤석열 대통령, 한동훈 비대위원장, 황상무 대통령 수석)
         - 호주대사 이종석의 사건으로 인한 수사가 진행 중이며, 이에 따라 출국이 불투명해지고 있다. (시작: 0.009, 끝: 146.954)
        2. 총선 공천과 비례대표 명단 발표 (키워드: 국민의 미래, 더불어민주연합, 조국 혁신당)
         - 민주당 내부에서 박용진 의원과 조수진 변호사 간의 공천을 둘러싼 정치적 갈등이 고조되고 있다. (시작: 186.937, 끝: 441.596)
        3. 강북을 중심으로 한 민주당 공천 논란 (키워드: 박영진 의원, 강북 공천, 한민수 후보)
         - 조국신당을 중심으로 한 정권심판론과 정책 대결이 치열하게 전개되고 있으며, 이는 선거 전략에 영향을 미칠 것으로 보인다. (시작: 973.268, 끝: 1049.48)

        주의:
        요약을 3개 이상 나열하지 마십시오.
        주제의 길이가 300초를 초과하지 않도록 주의하십시오.

        도움이 되는 답변:"""

    # 방법 1.
    # 요약을 먼저하고 (타임스탬프 미포함)
    # 스크립트에서 해당 주제에 관련된 부분을 찾기

    # 방법 2.
    # 문단 별로 스크립트를 요약하고 타임스탬프를 기입하기
    # 요약된 스크립트 리스트에서 중요하다고 생각하는 부분을 뽑아내기
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    # print(f'reduce_prompt: {reduce_prompt}')
    llm = ChatOpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY)

    # 1. Reduce chain
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="doc_summaries"
    )

    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000,
    )

    # 2. Map chain
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    try:
        sum_result = map_reduce_chain.run(split_docs)
        print(sum_result)
        train_path = "../fine_tuning/train.jsonl"

        # data = {
        #     "prompt": ,
        #
        # }

        return sum_result

    except Exception as e:
        print(e)
        print("To Long Text: " + file)
