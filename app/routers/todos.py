from fastapi import APIRouter

router = APIRouter()

@router.get('/todos', tags=['todos'])
async def get_all() -> str:
  return 'All todos route'