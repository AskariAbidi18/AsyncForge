import time

from app.services.task_service import (
    get_task,
    list_tasks_by_status,
    mark_task_running,
    mark_task_completed,
    handle_task_failure,
    reset_task_for_retry
)

from app.workers.handlers import get_handler
from app.utils.constants import Status


def get_next_pending_task():
    pending_tasks = list_tasks_by_status(Status.PENDING)

    if not pending_tasks:
        return None

    return pending_tasks[0]


def execute_task(task_id):
    task = get_task(task_id)

    result = mark_task_running(task_id)

    if result == "ignore":
        return

    try:
        handler = get_handler(task.task_type)

        handler(task.payload)

        mark_task_completed(task_id)

    except Exception as e:
        new_status = handle_task_failure(task_id, str(e))

        if new_status == Status.FAILED:
            reset_task_for_retry(task_id)


def worker_loop():
    print("Worker started...")

    while True:
        task = get_next_pending_task()

        if task is None:
            time.sleep(1)
            continue

        execute_task(task.task_id)
