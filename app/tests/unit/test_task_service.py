import pytest

from app.services.task_service import (
    create_task,
    get_task,
    list_tasks,
    mark_task_running,
    mark_task_completed,
    handle_task_failure,
    reset_task_for_retry,
)

from app.tests.factories import (
    task_factory,
    failed_task,
)

from app.utils.constants import (
    Status,
    TaskTypes,
)


# --------------------------------------------------
# get_task
# --------------------------------------------------

@pytest.mark.unit
def test_get_existing_task(db):

    task = task_factory()

    db.add(task)
    db.commit()

    fetched = get_task(db, task.task_id)

    assert fetched.task_id == task.task_id


@pytest.mark.unit
def test_get_missing_task(db):

    import uuid

    with pytest.raises(ValueError):
        get_task(db, uuid.uuid4())


# --------------------------------------------------
# list_tasks
# --------------------------------------------------

@pytest.mark.unit
def test_list_all_tasks(db):

    db.add(task_factory())
    db.add(task_factory())

    db.commit()

    tasks = list_tasks(db)

    assert len(tasks) == 2


@pytest.mark.unit
def test_list_tasks_by_status(db):

    db.add(task_factory(status=Status.PENDING))
    db.add(task_factory(status=Status.COMPLETED))

    db.commit()

    tasks = list_tasks(
        db,
        Status.COMPLETED,
    )

    assert len(tasks) == 1
    assert tasks[0].status == Status.COMPLETED


@pytest.mark.unit
def test_invalid_status_filter(db):

    with pytest.raises(ValueError):

        list_tasks(
            db,
            "HELLO"
        )


# --------------------------------------------------
# create_task
# --------------------------------------------------

@pytest.mark.unit
def test_create_task_success(db):

    task_id = create_task(
        db=db,
        task_type=TaskTypes.SEND_EMAIL,
        payload={
            "to": "bob@test.com",
            "body": "Hi"
        },
        max_retries=2,
    )

    task = get_task(
        db,
        task_id,
    )

    assert task.status == Status.PENDING
    assert task.retry_count == 0


# --------------------------------------------------
# mark running
# --------------------------------------------------

@pytest.mark.unit
def test_mark_running(db):

    task = task_factory()

    db.add(task)
    db.commit()

    mark_task_running(
        db,
        task.task_id,
    )

    db.refresh(task)

    assert task.status == Status.RUNNING


@pytest.mark.unit
def test_mark_running_invalid_state(db):

    task = task_factory(
        status=Status.COMPLETED
    )

    db.add(task)
    db.commit()

    with pytest.raises(ValueError) as exc:
        mark_task_running(
            db,
            task.task_id,
        )

    assert "Only pending tasks" in str(exc.value)

# --------------------------------------------------
# mark completed
# --------------------------------------------------

@pytest.mark.unit
def test_mark_completed(db):

    task = task_factory(
        status=Status.RUNNING
    )

    db.add(task)
    db.commit()

    mark_task_completed(
        db,
        task.task_id,
    )

    db.refresh(task)

    assert task.status == Status.COMPLETED


@pytest.mark.unit
def test_mark_completed_invalid_state(db):

    task = task_factory()

    db.add(task)
    db.commit()

    with pytest.raises(ValueError) as exc:
        mark_task_completed(
            db,
            task.task_id,
        )

    assert "Only running tasks" in str(exc.value)

# --------------------------------------------------
# failure
# --------------------------------------------------

@pytest.mark.unit
def test_failure_increments_retry(db):

    task = task_factory(
        status=Status.RUNNING,
        retry_count=0,
        max_retries=2,
    )

    db.add(task)
    db.commit()

    status = handle_task_failure(
        db,
        task.task_id,
        "Boom"
    )

    db.refresh(task)

    assert status == Status.FAILED
    assert task.retry_count == 1
    assert task.last_error == "Boom"


@pytest.mark.unit
def test_failure_moves_to_dead(db):

    task = task_factory(
        status=Status.RUNNING,
        retry_count=2,
        max_retries=2,
    )

    db.add(task)
    db.commit()

    status = handle_task_failure(
        db,
        task.task_id,
        "Boom"
    )

    db.refresh(task)

    assert status == Status.DEAD
    assert task.retry_count == 3


@pytest.mark.unit
def test_failure_invalid_state(db):

    task = task_factory(
        status=Status.COMPLETED
    )

    db.add(task)
    db.commit()

    with pytest.raises(ValueError) as exc:
        handle_task_failure(
            db,
            task.task_id,
            "Boom",
        )

    assert "Only running tasks" in str(exc.value)

# --------------------------------------------------
# retry
# --------------------------------------------------

@pytest.mark.unit
def test_retry_failed_task(db):

    task = failed_task()

    db.add(task)
    db.commit()

    reset_task_for_retry(
        db,
        task.task_id,
    )

    db.refresh(task)

    assert task.status == Status.PENDING
    assert task.last_error is None


@pytest.mark.unit
def test_retry_non_failed_task(db):

    task = task_factory(
        status=Status.COMPLETED
    )

    db.add(task)
    db.commit()

    with pytest.raises(ValueError):

        reset_task_for_retry(
            db,
            task.task_id,
        )
