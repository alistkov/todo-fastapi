from fastapi import APIRouter
from starlette import status
from passlib.context import CryptContext

from ..models.user import User
from ..database import db_dependency
from ..entities.user import CreateUserRequest, UpdateUserRequest, UserResponse

router = APIRouter(
    tags=["User"]
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(db: db_dependency, user: CreateUserRequest):
    user_model = User(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        password=bcrypt_context.hash(user.password)
    )
    db.add(user_model)
    db.commit()
    return user_model
