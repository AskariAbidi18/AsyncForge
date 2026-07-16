import time
import statistics
import pytest

from app.utils.constants import TaskTypes


@pytest.mark.performance
def test_post_latency(client):

    samples = []

    for i in range(50):

        start = time.perf_counter()

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

        end = time.perf_counter()

        assert response.status_code == 200

        samples.append((end - start) * 1000)

    print("\n------ POST /tasks Latency ------")
    print(f"Average : {statistics.mean(samples):.2f} ms")
    print(f"Median  : {statistics.median(samples):.2f} ms")
    print(f"Min     : {min(samples):.2f} ms")
    print(f"Max     : {max(samples):.2f} ms")
