from fastapi import APIRouter, Path, HTTPException, Depends
from starlette import status
from datetime import datetime
from typing import Annotated

from ..models.todos import Todo
from ..database import db_dependency
from ..entities.todos import CreateTodoRequest, TodoResponse, UpdateTodoRequest
from .user import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/todos', status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Todo).all()

@router.delete('/todos/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    todo_model = db.query(Todo).filter(Todo.id == id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')

    db.delete(todo_model)
    db.commit()
