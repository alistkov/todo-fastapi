from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status
from passlib.context import CryptContext
from typing import Annotated
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel

from ..models.user import User
from ..database import db_dependency
from ..entities.user import CreateUserRequest, UserResponse

load_dotenv()

class Token(BaseModel):
    access_token: str
    token_type: str

router = APIRouter(
    tags=["Auth"]
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='login')

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(username: str,
                        user_id: int,
                        role: str,
                        expires_delta: timedelta):
    encode = { 'sub': username, 'id': user_id, 'role': role }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({ 'exp': expires })
    return jwt.encode(encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=os.getenv('ALGORITHM'))
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user")

        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")


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

@router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return {
            'access_token': create_access_token(user.username, user.id, user.role, timedelta(minutes=20)),
            'token_type': 'bearer'
        }
