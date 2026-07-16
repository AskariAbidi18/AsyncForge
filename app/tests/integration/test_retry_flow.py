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
def test_retry_after_failure(db):

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
    ) as mock_handler:

        mock_handler.return_value.side_effect = Exception("Boom")

        execute_task(db, task_id)

    task = get_task(db, task_id)

    assert task.status == Status.PENDING
    assert task.retry_count == 1
    assert task.last_error is None


@pytest.mark.integration
def test_dead_after_max_retries(db):

    task_id = create_task(
        db=db,
        task_type=TaskTypes.SEND_EMAIL,
        payload={
            "to": "alice@test.com",
            "body": "Hello",
        },
        max_retries=0,
    )

    with patch(
        "app.workers.worker.get_handler"
    ) as mock_handler:

        mock_handler.return_value.side_effect = Exception("Boom")

        execute_task(db, task_id)

    task = get_task(db, task_id)

    assert task.status == Status.DEAD
    assert task.retry_count == 1
