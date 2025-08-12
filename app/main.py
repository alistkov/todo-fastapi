from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from .routers import todos, auth
from .database import engine

from . import models

app = FastAPI(
    title='Todo application',
    version='1.0.0'
)

models.Base.metadata.create_all(bind=engine)

app.include_router(todos.router)
app.include_router(auth.router)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        hide_models=True
    )
