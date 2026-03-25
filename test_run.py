import threading
import time

from app.workers.worker import worker_loop
from app.services.task_service import create_task
from app.utils.constants import TaskTypes

from app.redis_client import redis_client

redis_client.delete("asyncforge:tasks")


def start_worker():
    worker_loop()


# Start worker in background thread
worker_thread = threading.Thread(target=start_worker, daemon=True)
worker_thread.start()

time.sleep(1)

print("Creating tasks...")

create_task(
    TaskTypes.SEND_EMAIL,
    {"to": "alice@test.com", "body": "Hello Alice"},
    2
)

create_task(
    TaskTypes.PROCESS_IMAGE,
    {"image_path": "/tmp/photo.png"},
    3
)

create_task(
    TaskTypes.GENERATE_REPORT,
    {"report_id": "RPT-001"},
    1
)

create_task(
    TaskTypes.WEBHOOK_CALL,
    {"url": "https://example.com/webhook", "data": {"event": "test"}},
    2
)

print("Tasks submitted.")

# Keep process alive so worker thread keeps running
while True:
    time.sleep(5)
