from fastapi import APIRouter

from app.apis.routes import gpt

api_router = APIRouter()
api_router.include_router(gpt.router, prefix="/gpt", tags=["gpt"])
