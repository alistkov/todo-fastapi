from pydantic import BaseModel, Field
from datetime import datetime

class CreateTodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=5)

class UpdateTodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=5)
    completed: bool

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    completed: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int
