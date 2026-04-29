from fastapi import APIRouter
from app.schemas import IncidentCreate
from app.services.capm_service import create_incident

router = APIRouter(
    prefix="/incident",
    tags=["Incident"]
)


@router.post("/")
async def create_new_incident(data: IncidentCreate):

    payload = {
        "name": data.name,
        "email": data.email,
        "category": data.category,
        "priority": data.priority,
        "description": data.description,
        "suggestion": data.suggestion
    }

    response = await create_incident(payload)
    
    return {
        "message": "Incident created successfully",
        "incident_id": response.get("ID")
    }