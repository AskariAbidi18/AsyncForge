import time
from app.database import SessionLocal

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

def execute_task(db, task_id):

    try:
        task = get_task(db, task_id)

        print(f"[WORKER] executing {task_id} ({task.task_type})")

        mark_task_running(db, task_id)

        handler = get_handler(task.task_type)
        handler(task.payload)

        mark_task_completed(db, task_id)

        print(f"[WORKER] completed {task_id}")

    except ValueError as e:
        print(f"[WORKER] {e}")

    except Exception as e:
        print(f"[WORKER] failed {task_id}: {e}")

        try:
            handle_task_failure(
                db,
                task_id,
                str(e),
            )

            task = get_task(db, task_id)

            if task.status == Status.FAILED:
                print(f"[WORKER] retrying {task_id}")
                reset_task_for_retry(db, task_id)

        except Exception as inner:
            print(f"[WORKER] retry failed: {inner}")

def worker_loop():
    print("[WORKER] started")

    while True:
        task_id = get_next_task()

        print("[WORKER] received task:", task_id)

        if task_id:
            db = SessionLocal()

            try:
                execute_task(db, task_id)
            finally:
                db.close()
