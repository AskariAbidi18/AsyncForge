from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.task import (
    CreateTaskRequest,
    TaskCreatedResponse,
)
from app.services.task_service import create_task

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)

@router.post(
    "/",
    response_model = TaskCreatedResponse,
)
def create_new_task(
    request: CreateTaskRequest,
    db: Session = Depends(get_db),
):
    task_id = create_task(
        db = db,
        task_type = request.task_type,
        payload = request.payload,
        max_retries = request.max_retries
    )

    return TaskCreatedResponse(
        task_id = task_id
    )
