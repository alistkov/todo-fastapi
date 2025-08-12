from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, text, ForeignKey
from ..database import Base

class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    owner_id = Column(Integer, ForeignKey('users.id'), comment='Owner id')
