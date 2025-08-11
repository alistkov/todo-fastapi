from fastapi import APIRouter
from .entities import Todo
from . import models
from .database import db_dependency

router = APIRouter(
  prefix="/todos",
  tags=["Todos"]
)

@router.get('/')
async def get_all() -> str:
  return 'All todos route'

@router.post('/')
async def create_todo(todo: Todo, db: db_dependency):
  db_todo = models.Todo(title=todo.title)
  db.add(db_todo)
  db.commit()
  db.refresh(db_todo)
  return db_todo
