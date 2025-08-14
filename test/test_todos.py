import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime
from faker import Faker

from app.main import app
from app.database import Base, get_db
from app.routers.auth import get_current_user
from app.models.todos import Todo
from app.models.user import User
from app.entities.todos import CreateTodoRequest, TodoResponse, UpdateTodoRequest

load_dotenv()

engine = create_engine(os.getenv('TEST_DATABASE_CONNECTION_STRING'))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
fake = Faker()

@pytest.fixture
def test_user():
    user = User(
        email=fake.email(),
        username=fake.user_name(),
        first_name=fake.name(),
        last_name=fake.last_name(),
        role='admin',
        password=fake.password(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    # First delete all todos for this user to avoid foreign key constraint
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos WHERE owner_id = :user_id"), {"user_id": user.id})
        connection.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user.id})
        connection.commit()

@pytest.fixture
def current_user_override(test_user):
    def mock_get_current_user():
        return {
            'id': test_user.id,
            'username': test_user.username,
            'user_role': test_user.role
        }
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    # Only remove the get_current_user override, keep get_db override
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]

@pytest.fixture
def test_todo(test_user):
    todo = CreateTodoRequest(title="Learn FastApi", description="Todo description", priority=4)
    todo_model = Todo(**todo.model_dump(), owner_id=test_user.id)
    db = TestingSessionLocal()
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    yield todo_model
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos WHERE id = :todo_id"), {"todo_id": todo_model.id})
        connection.commit()



def test_read_all_authenticated(test_todo, current_user_override):
    response = client.get('/todos')
    assert response.status_code == status.HTTP_200_OK
    todos = response.json()
    assert len(todos) == 1

def test_read_one_authenticated(test_todo, current_user_override):
    response = client.get(f'/todos/{test_todo.id}')
    assert response.status_code == status.HTTP_200_OK
    todo = response.json()
    assert todo.get('id') == test_todo.id

def test_read_one_not_found(test_todo, current_user_override):
    response = client.get(f'/todos/{test_todo.id + 1}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': f'Todo with #{test_todo.id + 1} not found'}

def test_create_todo(test_user, current_user_override):
    request_data = CreateTodoRequest(title="Todo title for test", description="Todo description for test", priority=2)
    response = client.post('/todos', json=request_data.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    todo: TodoResponse = TodoResponse(**response.json())
    assert todo.title == request_data.title
    assert todo.completed is False
    assert todo.owner_id == test_user.id

def test_update_todo(test_todo, test_user, current_user_override):
    request_data = UpdateTodoRequest(title='Updated title', description='Updated description', priority=3, completed=True)
    response = client.put(f'/todos/{test_todo.id}', json=request_data.model_dump())
    assert response.status_code == status.HTTP_200_OK
    todo = TodoResponse(**response.json())
    assert todo.completed is True
    assert todo.title == request_data.title
    assert todo.owner_id == test_user.id

def test_update_todo_not_found(test_todo, test_user, current_user_override):
    request_data = UpdateTodoRequest(title='Updated title', description='Updated description', priority=3, completed=True)
    response = client.put(f'/todos/{test_todo.id + 1}', json=request_data.model_dump())
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': f'Todo with #{test_todo.id + 1} not found'}


def test_delete_todo(test_todo, current_user_override):
    response = client.delete(f'/todos/{test_todo.id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo = db.query(Todo).filter(Todo.id == test_todo.id).first()
    assert todo is None

def test_delete_todo_not_found(test_todo, current_user_override):
    response = client.delete(f'/todos/{test_todo.id + 1}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': f'Todo with #{test_todo.id + 1} not found'}
