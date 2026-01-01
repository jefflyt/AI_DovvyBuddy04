from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(payload: dict):
    # Placeholder response
    return {"reply": "This is a placeholder chat response", "received": payload}
