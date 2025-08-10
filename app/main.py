from fastapi import FastAPI, Depends
from .routers import router

from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(router)
