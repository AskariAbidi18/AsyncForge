import time
import pytest

from app.utils.constants import TaskTypes


@pytest.mark.performance
def test_task_creation_throughput(client):

    NUM_REQUESTS = 200

    start = time.perf_counter()

    for i in range(NUM_REQUESTS):

        response = client.post(
            "/tasks/",
            json={
                "task_type": TaskTypes.SEND_EMAIL,
                "payload": {
                    "to": f"user{i}@test.com",
                    "body": "Hello",
                },
                "max_retries": 2,
            },
        )

        assert response.status_code == 200

    elapsed = time.perf_counter() - start

    throughput = NUM_REQUESTS / elapsed

    print("\n------ Throughput ------")
    print(f"Requests : {NUM_REQUESTS}")
    print(f"Time      : {elapsed:.2f} sec")
    print(f"Throughput: {throughput:.2f} req/sec")
