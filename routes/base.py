from fastapi import APIRouter
from routes import PREFIX
router = APIRouter(prefix=PREFIX)

@router.get("/ping")
async def ping():
    return {"message": "pong"}
