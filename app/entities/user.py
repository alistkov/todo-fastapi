from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CreateUserRequest(BaseModel):
    email: str = Field(min_length=3)
    username: str = Field(min_length=3)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    password: str = Field(min_length=5, max_length=16)
    role: str = Field(min_length=3)
    phone_number: Optional[str] = None

class UpdateUserRequest(BaseModel):
    email: str = Field(min_length=3)
    username: str = Field(min_length=3)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    is_active: bool
    role: str = Field(min_length=3)
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
    phone_number: Optional[str] = None

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=5, max_length=16)
