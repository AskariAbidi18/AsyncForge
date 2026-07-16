import uuid

from app.models.task import Task
from app.utils.constants import (
    Status,
    TaskTypes,
)


def task_factory(
    *,
    task_type=TaskTypes.SEND_EMAIL,
    status=Status.PENDING,
    payload=None,
    retry_count=0,
    max_retries=2,
    last_error=None,
):

    if payload is None:
        payload = {
            "to": "alice@test.com",
            "body": "Hello"
        }

    return Task(
        task_id=uuid.uuid4(),
        task_type=task_type,
        payload=payload,
        status=status,
        retry_count=retry_count,
        max_retries=max_retries,
        last_error=last_error,
    )


def failed_task():
    return task_factory(
        status=Status.FAILED,
        retry_count=1,
        last_error="Failure",
    )


def running_task():
    return task_factory(
        status=Status.RUNNING,
    )


def completed_task():
    return task_factory(
        status=Status.COMPLETED,
    )


def dead_task():
    return task_factory(
        status=Status.DEAD,
        retry_count=3,
        last_error="Retries exhausted",
    )
