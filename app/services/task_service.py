import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.queue.producer import enqueue_task
from app.utils.constants import Status, TaskTypes
from app.utils.time import now


def get_task(db: Session, task_id: UUID) -> Task:
    task = (
        db.query(Task)
        .filter(Task.task_id == task_id)
        .first()
    )

    if task is None:
        raise ValueError(f"Task '{task_id}' does not exist.")

    return task


def list_tasks(
    db: Session,
    status: str | None = None,
) -> list[Task]:
    if status is not None:
        if status not in vars(Status).values():
            raise ValueError(f"Invalid status '{status}'.")

        return (
            db.query(Task)
            .filter(Task.status == status)
            .all()
        )

    return db.query(Task).all()


def is_serializable(payload: dict) -> bool:
    try:
        json.dumps(payload)
        return True
    except (TypeError, ValueError):
        return False


def create_task(
    db: Session,
    task_type: str,
    payload: dict,
    max_retries: int,
) -> UUID:

    if task_type not in vars(TaskTypes).values():
        raise ValueError(f"Invalid task type '{task_type}'.")

    if not is_serializable(payload):
        raise ValueError("Payload must be JSON serializable.")

    if max_retries < 0:
        raise ValueError("max_retries must be non-negative.")

    task = Task(
        task_type=task_type,
        payload=payload,
        max_retries=max_retries,
    )

    try:
        db.add(task)
        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise

    enqueue_task(task.task_id)

    return task.task_id


def mark_task_running(
    db: Session,
    task_id: UUID,
) -> Task:

    task = get_task(db, task_id)

    if task.status != Status.PENDING:
        raise ValueError(
            "Only pending tasks can be marked as running."
        )

    try:
        task.status = Status.RUNNING
        task.updated_at = now()

        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise

    return task


def mark_task_completed(
    db: Session,
    task_id: UUID,
) -> Task:

    task = get_task(db, task_id)

    if task.status != Status.RUNNING:
        raise ValueError(
            "Only running tasks can be completed."
        )

    try:
        task.status = Status.COMPLETED
        task.updated_at = now()

        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise

    return task


def handle_task_failure(
    db: Session,
    task_id: UUID,
    error_message: str,
) -> str:

    task = get_task(db, task_id)

    if task.status != Status.RUNNING:
        raise ValueError(
            "Only running tasks can fail."
        )

    try:
        task.retry_count += 1
        task.last_error = error_message
        task.updated_at = now()

        if task.retry_count > task.max_retries:
            task.status = Status.DEAD
        else:
            task.status = Status.FAILED

        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise

    return task.status


def reset_task_for_retry(
    db: Session,
    task_id: UUID,
) -> Task:

    task = get_task(db, task_id)

    if task.status != Status.FAILED:
        raise ValueError(
            "Only failed tasks can be retried."
        )

    try:
        task.status = Status.PENDING
        task.last_error = None
        task.updated_at = now()

        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise

    enqueue_task(task.task_id)

    return task

def delete_task(
    db: Session,
    task_id: UUID,
) -> None:

    task = get_task(db, task_id)

    if task.status == Status.RUNNING:
        raise ValueError(
            "Running tasks cannot be deleted."
        )

    try:
        db.delete(task)
        db.commit()

    except Exception:
        db.rollback()
        raise
