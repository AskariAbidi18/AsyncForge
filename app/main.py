from fastapi import FastAPI

from app.api.tasks import router as task_router
from app.database import Base, engine

import app.models.task

app = FastAPI(
    title = "AsyncForge",
    version = "0.1.0",
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind = engine)

app.include_router(task_router)

@app.get("/")
def health():
    return {
        "status" : "running"
    }
