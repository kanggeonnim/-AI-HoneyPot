# demo=fast-apis > schemas > gpt_sch.py 파일 생성
from pydantic import BaseModel


# 요청시
class GptRequestSch(BaseModel):
    content: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "content": "Base Tesla Model 3 Inventory has $2,410 discount and now Qualifies for $7,500 Tax Credit"
            }
        }


# 결과를 응답하는 경우
class GptResponseSch(BaseModel):
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "summary": "openai 'gpt-3.5-turbo-0125'을 사용하여 요약한 메시지 내용 입니다",
            }
        }
