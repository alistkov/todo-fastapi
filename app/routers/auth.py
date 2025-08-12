from fastapi import APIRouter
from starlette import status

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_user():
  return { 'user': 'authenticate' }
