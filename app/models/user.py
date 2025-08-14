from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, text, func
from datetime import datetime

from ..database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    password = Column(String)
    role = Column(String)
    phone_number = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    def __init__(self, **data):
            super().__init__(**data)
            self.updated_at = datetime.utcnow()

    class Config:
        orm_mode = True
