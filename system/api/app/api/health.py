# api/app/api/health.py
from fastapi import APIRouter # type: ignore

router = APIRouter()

@router.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "incidentiq-api"
    }
