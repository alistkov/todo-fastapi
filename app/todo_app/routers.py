from fastapi import APIRouter, Path, HTTPException
from starlette import status
from datetime import datetime

from .models import Todo
from .database import db_dependency
from .entities import CreateTodoRequest, TodoResponse, UpdateTodoRequest

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

@router.get('/', status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def get_all(db: db_dependency):
    return db.query(Todo).all()

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def get_todo_by_id(db: db_dependency, id: int = Path(gt=0)) -> TodoResponse:
    todo_model = db.query(Todo).filter(Todo.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')
    return todo_model

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(db: db_dependency, body: CreateTodoRequest) -> TodoResponse:
    todo_model = Todo(**body.model_dump())
    db.add(todo_model)
    db.commit()
    return todo_model

@router.post('/{id}', status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(db: db_dependency,
                      body: UpdateTodoRequest,
                      id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')

    todo_model.title = body.title
    todo_model.description = body.description
    todo_model.priority = body.priority
    todo_model.completed = body.completed
    todo_model.updated_at = datetime.now()

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return todo_model

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delet_todo(db: db_dependency, id: int = Path(gt=0)):
    # todo_model = db.query(Todo).filter(Todo.id == id).first()
    todo_model = db.get(Todo, id)
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'Todo with #{id} not found')

    db.delete(todo_model)
    db.commit()


