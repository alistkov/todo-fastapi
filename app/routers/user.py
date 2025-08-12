from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from passlib.context import CryptContext
from typing import Annotated

from ..models.user import User
from ..database import db_dependency
from ..entities.user import CreateUserRequest, UpdateUserRequest, UserResponse

router = APIRouter(
    tags=["User"]
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return True

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

@router.post('/login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    if not authenticate_user(form_data.username, form_data.password, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return 'Successfull!'
