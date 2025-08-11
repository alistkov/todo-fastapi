from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.todo_app.routers import router
from app.todo_app.database import engine

from app.todo_app import models

app = FastAPI(
    title='Todo application',
    version='1.0.0'
)

models.Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        hide_models=True
    )
