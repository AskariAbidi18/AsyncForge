import time

from app.services.task_service import (
    get_task,
    mark_task_running,
    mark_task_completed,
    handle_task_failure,
    reset_task_for_retry
)

from app.workers.handlers import get_handler
from app.utils.constants import Status
from app.queue.consumer import get_next_task
from app.queue.producer import enqueue_task

def execute_task(task_id):

    try:
        task = get_task(task_id)
    except ValueError:
        print(f"[WORKER] task {task_id} not found in memory, skipping")
        return

    print(f"[WORKER] executing {task_id} ({task.task_type})")

    result = mark_task_running(task_id)

    if result == "ignore":
        print(f"[WORKER] ignoring {task_id}")
        return

    try:
        handler = get_handler(task.task_type)
        handler(task.payload)

        mark_task_completed(task_id)

        print(f"[WORKER] completed {task_id}")

    except Exception as e:
        print(f"[WORKER] failed {task_id}: {e}")

        new_status = handle_task_failure(task_id, str(e))

        if new_status == Status.FAILED:
            print(f"[WORKER] retrying {task_id}")
            reset_task_for_retry(task_id)
            enqueue_task(task_id)

def worker_loop():
    print("[WORKER] started")

    while True:
        task_id = get_next_task()

        print("[WORKER] received task:", task_id)

        if task_id:
            execute_task(task_id)
