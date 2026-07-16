import pytest

from app.services.task_service import (
    is_serializable,
    create_task,
)

from app.utils.constants import TaskTypes


# ---------- is_serializable ----------

def test_serializable_dict():
    payload = {
        "name": "Askari",
        "age": 20,
    }

    assert is_serializable(payload) is True


def test_serializable_nested_dict():
    payload = {
        "user": {
            "name": "Askari",
            "skills": ["Python", "FastAPI"],
        }
    }

    assert is_serializable(payload)


def test_non_serializable_object():

    class Dummy:
        pass

    payload = {
        "obj": Dummy()
    }

    assert is_serializable(payload) is False


# ---------- create_task validation ----------

@pytest.mark.unit
def test_invalid_task_type(db):

    with pytest.raises(ValueError) as exc:

        create_task(
            db=db,
            task_type="INVALID_TASK",
            payload={},
            max_retries=2,
        )

    assert "Invalid task type" in str(exc.value)


@pytest.mark.unit
def test_negative_retry_count(db):

    with pytest.raises(ValueError) as exc:

        create_task(
            db=db,
            task_type=TaskTypes.SEND_EMAIL,
            payload={},
            max_retries=-1,
        )

    assert "non-negative" in str(exc.value)


@pytest.mark.unit
def test_non_serializable_payload(db):

    class Dummy:
        pass

    payload = {
        "dummy": Dummy()
    }

    with pytest.raises(ValueError) as exc:

        create_task(
            db=db,
            task_type=TaskTypes.SEND_EMAIL,
            payload=payload,
            max_retries=2,
        )

    assert "JSON serializable" in str(exc.value)


@pytest.mark.unit
def test_valid_create_task(db):

    task_id = create_task(
        db=db,
        task_type=TaskTypes.SEND_EMAIL,
        payload={
            "to": "alice@test.com",
            "body": "Hello",
        },
        max_retries=2,
    )

    assert task_id is not None
