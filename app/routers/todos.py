from fastapi import APIRouter, Path, HTTPException, Depends
from starlette import status
from datetime import datetime
from typing import Annotated

from ..models.todos import Todo
from ..database import db_dependency
from ..entities.todos import CreateTodoRequest, TodoResponse, UpdateTodoRequest
from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def get_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def get_todo_by_id(user: user_dependency, db: db_dependency, id: int = Path(gt=0)) -> TodoResponse:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    todo_model = db.query(Todo).filter(Todo.id == id)\
        .filter(Todo.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')
    return todo_model

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(user: user_dependency,
                      db: db_dependency,
                      body: CreateTodoRequest) -> TodoResponse:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    todo_model = Todo(**body.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()
    return todo_model

@router.put('/{id}', status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(user: user_dependency,
                      db: db_dependency,
                      body: UpdateTodoRequest,
                      id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    todo_model = db.query(Todo).filter(Todo.id == id)\
        .filter(Todo.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')

    for field, value in body.dict(exclude_unset=True).items():
        setattr(todo_model, field, value)

    db.commit()
    db.refresh(todo_model)

    return todo_model

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                     db: db_dependency,
                     id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todo).filter(Todo.id == id)\
        .filter(Todo.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')

    db.delete(todo_model)
    db.commit()


