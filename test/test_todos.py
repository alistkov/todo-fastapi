import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime

from app.main import app
from app.database import Base, get_db
from app.routers.auth import get_current_user
from app.models.todos import Todo
from app.models.user import User
from app.entities.todos import CreateTodoRequest, TodoResponse

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

@pytest.fixture
def test_user():
    user = User(
        email='j.doe@example.com',
        username='j.doe',
        first_name='John',
        last_name='Doe',
        role='admin',
        password='hashed_password',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    print(user.id)
    yield user
    with engine.connect() as connection:
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
    app.dependency_overrides.clear() # Clean up overrides after the test

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

    # Verify the returned todo matches our test todo
    returned_todo = todos[0]
    assert type(returned_todo is TodoResponse)
    assert returned_todo['id'] == test_todo.id
    assert returned_todo['title'] == test_todo.title
    assert returned_todo['description'] == test_todo.description
    assert returned_todo['priority'] == test_todo.priority
    assert returned_todo['completed'] == test_todo.completed
    assert returned_todo['owner_id'] == test_todo.owner_id
