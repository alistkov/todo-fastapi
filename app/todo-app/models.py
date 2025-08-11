from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, text
from database import Base

class Todo(Base):
  __tablename__ = 'todos'

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String, index=True)
  description = Column(String)
  proiority = Column(Integer)
  complete = Column(Boolean, default=False)
  created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
  updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))