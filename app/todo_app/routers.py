from fastapi import APIRouter, Path
from fastapi.exceptions import HTTPException
from starlette import status

from .models import Todo
from .database import db_dependency

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency):
    return db.query(Todo).all()

@router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_todo_by_id(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')
