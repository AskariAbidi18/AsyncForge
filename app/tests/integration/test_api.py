import pytest

from app.utils.constants import (
    Status,
    TaskTypes,
)


# --------------------------------------------------
# CREATE TASK
# --------------------------------------------------

@pytest.mark.integration
def test_create_task(client):

    response = client.post(
        "/tasks/",
        json={
            "task_type": TaskTypes.SEND_EMAIL,
            "payload": {
                "to": "alice@test.com",
                "body": "Hello"
            },
            "max_retries": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "task_id" in body


@pytest.mark.integration
def test_invalid_task_type(client):

    response = client.post(
        "/tasks/",
        json={
            "task_type": "INVALID",
            "payload": {},
            "max_retries": 2,
        },
    )

    assert response.status_code == 400


# --------------------------------------------------
# GET TASK
# --------------------------------------------------

@pytest.mark.integration
def test_get_existing_task(client):

    response = client.post(
        "/tasks/",
        json={
            "task_type": TaskTypes.SEND_EMAIL,
            "payload": {
                "to": "bob@test.com",
                "body": "Hi"
            },
            "max_retries": 2,
        },
    )

    task_id = response.json()["task_id"]

    response = client.get(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 200

    task = response.json()

    assert task["task_id"] == task_id


@pytest.mark.integration
def test_get_invalid_task(client):

    response = client.get(
        "/tasks/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


# --------------------------------------------------
# LIST TASKS
# --------------------------------------------------

@pytest.mark.integration
def test_list_tasks(client):

    client.post(
        "/tasks/",
        json={
            "task_type": TaskTypes.SEND_EMAIL,
            "payload": {
                "to": "one@test.com",
                "body": "Hello"
            },
            "max_retries": 2,
        },
    )

    client.post(
        "/tasks/",
        json={
            "task_type": TaskTypes.GENERATE_REPORT,
            "payload": {
                "report_id": "sales"
            },
            "max_retries": 2,
        },
    )

    response = client.get("/tasks/")

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2


# --------------------------------------------------
# FILTER
# --------------------------------------------------

@pytest.mark.integration
def test_filter_completed(client):

    response = client.get(
        "/tasks/?status=COMPLETED"
    )

    assert response.status_code == 200


@pytest.mark.integration
def test_invalid_status_filter(client):

    response = client.get(
        "/tasks/?status=HELLO"
    )

    assert response.status_code == 400
