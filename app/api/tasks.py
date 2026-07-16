from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.task import (
    CreateTaskRequest,
    MessageResponse,
    TaskCreatedResponse,
    TaskResponse,
)
from app.services.task_service import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    reset_task_for_retry,
)

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
    try:
        task_id = create_task(
            db = db,
            task_type = request.task_type,
            payload = request.payload,
            max_retries = request.max_retries
        )
        return TaskCreatedResponse(
            task_id = task_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code = 400,
            detail = str(e)
        )

@router.get(
    "/{task_id}",
    response_model = TaskResponse,
)
def get_task_by_id(
    task_id : UUID,
    db : Session = Depends(get_db),
):
    try:
        task = get_task(db, task_id)
        return TaskResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(
            status_code = 404,
            detail = str(e)
        )

@router.get(
    "/",
    response_model = list[TaskResponse],
)
def list_all_tasks(
    status: str | None = None,
    db : Session = Depends(get_db),
):
    try:
        tasks = list_tasks(db, status)
        return tasks
    except ValueError as e:
        raise HTTPException(
            status_code = 400,
            detail = str(e)
        )

@router.patch(
    "/{task_id}/retry",
    response_model = TaskResponse,
)
def retry_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        task = reset_task_for_retry(db, task_id)
        return task
    except ValueError as e:

        message = str(e)

        if "does not exist" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=409,
            detail=message,
        )

@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
)
def delete_existing_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        delete_task(db, task_id)

        return MessageResponse(
            message="Task deleted successfully."
        )

    except ValueError as e:
        message = str(e)

        if "does not exist" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=409,
            detail=message,
        )
