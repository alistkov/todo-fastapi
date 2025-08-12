from pydantic import BaseModel, Field
from datetime import datetime

class CreateUserRequest(BaseModel):
    email: str = Field(min_length=3)
    username: str = Field(min_length=3)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    password: str = Field(min_length=5, max_length=16)
    role: str = Field(min_length=3)

class UpdateUserRequest(BaseModel):
    email: str = Field(min_length=3)
    username: str = Field(min_length=3)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    is_active: bool
    password: str = Field(min_length=3)
    role: str = Field(min_length=3)

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    password: str
    role: str
    created_at: datetime
    updated_at: datetime
