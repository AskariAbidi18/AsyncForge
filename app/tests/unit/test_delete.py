import pytest

from app.services.task_service import delete_task, get_task

from app.tests.factories import (
    task_factory,
    running_task,
)

from app.utils.constants import Status


@pytest.mark.unit
@pytest.mark.unit
def test_delete_pending_task(db):

    task = task_factory()

    db.add(task)
    db.commit()

    delete_task(
        db,
        task.task_id,
    )

    with pytest.raises(ValueError):
        get_task(
            db,
            task.task_id,
        )

@pytest.mark.unit
def test_delete_completed_task(db):

    task = task_factory(
        status=Status.COMPLETED,
    )

    db.add(task)
    db.commit()

    delete_task(
        db,
        task.task_id,
    )

    with pytest.raises(ValueError):
        get_task(
            db,
            task.task_id,
        )

@pytest.mark.unit
def test_delete_running_task(db):

    task = running_task()

    db.add(task)
    db.commit()

    with pytest.raises(ValueError) as exc:

        delete_task(
            db,
            task.task_id,
        )

    assert "running" in str(exc.value).lower()


@pytest.mark.unit
def test_delete_nonexistent_task(db):

    import uuid

    with pytest.raises(ValueError):

        delete_task(
            db,
            uuid.uuid4(),
        )
