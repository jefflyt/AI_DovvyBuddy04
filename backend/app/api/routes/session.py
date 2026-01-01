from fastapi import APIRouter

router = APIRouter()


@router.get("/sessions")
async def list_sessions():
    return {"sessions": []}

@router.post("/sessions")
async def create_session(payload: dict):
    # Placeholder: would create session using SessionRepository
    return {"id": "placeholder", "data": payload}
