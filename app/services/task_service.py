from sqlalchemy.orm import Session

from app.models.task import Task
from app.utils.constants import Status, TaskTypes
from app.utils.time import now
from app.queue.producer import enqueue_task

import json


def get_task(db: Session, task_id):
    task = (
        db.query(Task)
        .filter(Task.task_id == task_id)
        .first()
    )

    if not task:
        raise ValueError(f"Task with id {task_id} does not exist")

    return task


def list_tasks_by_status(db: Session, status):
    if status not in vars(Status).values():
        raise ValueError(f"Invalid status: {status}")

    return (
        db.query(Task)
        .filter(Task.status == status)
        .all()
    )


def is_serializable(payload):
    try:
        json.dumps(payload)
        return True
    except (TypeError, ValueError):
        return False


def create_task(db: Session, task_type, payload, max_retries):
    if task_type not in vars(TaskTypes).values():
        raise ValueError(f"Invalid task type: {task_type}")

    if not is_serializable(payload):
        raise ValueError("Payload must be json serializable")

    if max_retries < 0:
        raise ValueError("Max Retries must be a non-negative integer")

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


def mark_task_running(db: Session, task_id):
    task = get_task(db, task_id)

    if task.status != Status.PENDING:
        return "ignore"

    try:
        task.status = Status.RUNNING
        task.updated_at = now()

        db.commit()
        db.refresh(task)
    except Exception:
        db.rollback()
        raise


def mark_task_completed(db: Session, task_id):
    task = get_task(db, task_id)

    if task.status != Status.RUNNING:
        return "ignore"

    try:
        task.status = Status.COMPLETED
        task.updated_at = now()

        db.commit()
        db.refresh(task)
    except Exception:
        db.rollback()
        raise


def handle_task_failure(db: Session, task_id, error_message):
    task = get_task(db, task_id)

    if task.status != Status.RUNNING:
        return "ignore"

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

        return task.status

    except Exception:
        db.rollback()
        raise


def reset_task_for_retry(db: Session, task_id):
    task = get_task(db, task_id)

    if task.status != Status.FAILED:
        return "ignore"

    try:
        task.status = Status.PENDING
        task.updated_at = now()

        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise
    