import pytest
from unittest.mock import patch

from app.services.task_service import (
    create_task,
    get_task,
)

from app.workers.worker import execute_task

from app.utils.constants import (
    Status,
    TaskTypes,
)


@pytest.mark.integration
def test_worker_executes_successfully(db):

    task_id = create_task(
        db=db,
        task_type=TaskTypes.SEND_EMAIL,
        payload={
            "to": "alice@test.com",
            "body": "Hello",
        },
        max_retries=2,
    )

    with patch(
        "app.workers.worker.get_handler"
    ) as mock:

        mock.return_value.return_value = None

        execute_task(db, task_id)

    task = get_task(db, task_id)

    assert task.status == Status.COMPLETED
    assert task.retry_count == 0


@pytest.mark.integration
def test_worker_invalid_handler(db):

    task_id = create_task(
        db=db,
        task_type=TaskTypes.SEND_EMAIL,
        payload={
            "to": "alice@test.com",
            "body": "Hello",
        },
        max_retries=2,
    )

    with patch(
        "app.workers.worker.get_handler"
    ) as mock:

        mock.side_effect = ValueError("No handler")

        execute_task(db, task_id)

    task = get_task(db, task_id)

    assert task.status == Status.PENDING


@pytest.mark.integration
def test_worker_handler_exception(db):

    task_id = create_task(
        db=db,
        task_type=TaskTypes.SEND_EMAIL,
        payload={
            "to": "alice@test.com",
            "body": "Hello",
        },
        max_retries=2,
    )

    with patch(
        "app.workers.worker.get_handler"
    ) as mock:

        mock.return_value.side_effect = RuntimeError("Failure")

        execute_task(db, task_id)

    task = get_task(db, task_id)

    assert task.retry_count == 1
