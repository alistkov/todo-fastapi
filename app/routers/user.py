from fastapi import APIRouter, Path, HTTPException, Depends
from starlette import status
from datetime import datetime
from typing import Annotated
from passlib.context import CryptContext

from ..database import db_dependency
from ..entities.user import UserResponse, UserVerification, UpdateUserRequest
from ..models.user import User
from .auth import get_current_user

router = APIRouter(
    tags=["User"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get('/profile', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    return db.query(User).filter(User.id == user.get('id')).first()

@router.put('/profile', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_profile(user: user_dependency, db: db_dependency, body: UpdateUserRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    user_model.email = body.email
    user_model.username = body.username
    user_model.first_name = body.first_name
    user_model.last_name = body.last_name
    user_model.is_active = body.is_active
    user_model.role = body.role

    db.add(user_model)
    db.commit()
    return user_model

@router.put('/change-password', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.password):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user_model.password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return user_model
