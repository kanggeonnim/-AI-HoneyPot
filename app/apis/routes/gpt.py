from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.models import GptResponseSch, GptRequestSch
from app.config.config import settings
from openai import OpenAI
import json

router = APIRouter()


@router.post("/summary/{category}", response_model=GptResponseSch)
async def translate_by_gpt_router(category: str, req: GptRequestSch):
    # 선택한 카테고리에 따라 프롬프트 설정
    prompt_map = {
        "bill": settings.GPT_PROMPT_BILL,
        "issue": settings.GPT_PROMPT_ISSUE
    }
    pre_prompt = prompt_map.get(category)
    if not pre_prompt:
        return JSONResponse(content={"error": f"Invalid category: {category}"}, status_code=400)

    # APIs 호출
    openai_result = await translate_by_openai(req, pre_prompt)

    # 결과를 리턴합니다
    try:
        json_data = json.loads(openai_result)
    except json.JSONDecodeError as e:
        json_data = {"error": "Failed to decode JSON"}
        print(e)
        return openai_result

    return JSONResponse(content=json_data)


async def translate_by_openai(req: GptRequestSch, pre_prompt: str):
    # OpenAI API 키 인증
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # 모델 - GPT 3.5 Turbo 선택
    model = "gpt-3.5-turbo-0125"

    # 메시지 설정
    messages = [{
        "role": "user",
        "content": pre_prompt + req.content,
    }]

    # ChatGPT API 호출
    response = client.chat.completions.create(
        model=model, messages=messages
    )
    openai_result = response.choices[0].message.content

    return openai_result
