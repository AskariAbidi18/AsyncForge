import concurrent.futures
import statistics
import time

import requests

from app.utils.constants import TaskTypes

BASE_URL = "http://localhost:8000"

NUM_REQUESTS = 200
NUM_WORKERS = 20

payload = {
    "task_type": TaskTypes.SEND_EMAIL,
    "payload": {
        "to": "benchmark@test.com",
        "body": "Benchmark",
    },
    "max_retries": 2,
}


def send_request(i):

    start = time.perf_counter()

    response = requests.post(
        f"{BASE_URL}/tasks/",
        json={
            **payload,
            "payload": {
                "to": f"user{i}@test.com",
                "body": "Benchmark",
            },
        },
    )

    elapsed = (time.perf_counter() - start) * 1000

    return response.status_code, elapsed


def main():

    print("=" * 60)
    print("AsyncForge Load Benchmark")
    print("=" * 60)
    print(f"Workers   : {NUM_WORKERS}")
    print(f"Requests  : {NUM_REQUESTS}")
    print()

    overall_start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=NUM_WORKERS
    ) as executor:

        results = list(
            executor.map(send_request, range(NUM_REQUESTS))
        )

    total_time = time.perf_counter() - overall_start

    statuses = [status for status, _ in results]
    latencies = [latency for _, latency in results]

    success = statuses.count(200)
    failures = len(statuses) - success

    throughput = NUM_REQUESTS / total_time

    print("=" * 60)
    print("Results")
    print("=" * 60)

    print(f"Successful Requests : {success}")
    print(f"Failed Requests     : {failures}")
    print(f"Total Time          : {total_time:.2f} sec")
    print(f"Throughput          : {throughput:.2f} req/sec")
    print()

    print("Latency")
    print(f"Average             : {statistics.mean(latencies):.2f} ms")
    print(f"Median              : {statistics.median(latencies):.2f} ms")
    print(f"Minimum             : {min(latencies):.2f} ms")
    print(f"Maximum             : {max(latencies):.2f} ms")

    if failures:
        print("\nWARNING: Some requests failed.")


if __name__ == "__main__":
    main()
