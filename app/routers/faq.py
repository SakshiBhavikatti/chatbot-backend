from fastapi import APIRouter
from app.services.capm_service import fetch_faqs

router = APIRouter(
    prefix="/faqs",
    tags=["FAQs"]
)


@router.get("/")
async def get_faqs():
    return await fetch_faqs()