import threading
import time

from app.workers.worker import worker_loop
from app.services.task_service import create_task
from app.utils.constants import TaskTypes


def start_worker():
    worker_loop()


# start worker in background thread
worker_thread = threading.Thread(target=start_worker, daemon=True)
worker_thread.start()

# give worker a moment to start
time.sleep(1)

print("Creating tasks...")

create_task(TaskTypes.SEND_EMAIL, {"to": "alice@test.com", "body": "Hello"}, 2)
create_task(TaskTypes.PROCESS_IMAGE, {"image_path": "/tmp/test.png"}, 3)
create_task(TaskTypes.GENERATE_REPORT, {"report_id": "R1"}, 1)
create_task(TaskTypes.WEBHOOK_CALL, {"url": "https://test.com", "data": {"a": 1}}, 2)

print("Tasks submitted.")

# keep program alive so worker can run
while True:
    time.sleep(5)