from fastapi import APIRouter
from sqlalchemy.orm import Session

from .models import Todo
from .database import db_dependency

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

@router.get('/')
async def get_all(db: db_dependency):
    return db.query(Todo).all()
