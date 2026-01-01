from fastapi import APIRouter

router = APIRouter()

@router.post("/leads")
async def create_lead(payload: dict):
    # Placeholder: would use LeadRepository to persist
    return {"id": "placeholder-lead-id", "data": payload}
