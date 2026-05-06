from fastapi import APIRouter
from app.services import query_menu

router = APIRouter()

@router.post("/chat")
async def chat(query: str, use_cloud: bool = True):
    answer = query_menu(query, use_cloud)
    return {"answer": answer}
  
