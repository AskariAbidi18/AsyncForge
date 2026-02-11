from app.models.task import Task
from app.utils.constants import Status, TaskTypes
from app.utils.time import now
import json

task_store = {}

def get_task(task_id):
    task = task_store.get(task_id)

    if not task:
        raise ValueError(f"Task with id {task_id} does not exist")
    
    return task

def list_tasks_by_status(status):
    if status not in vars(Status).values():
        raise ValueError(f"Invalid status: {status}")
    
    return [task for task in task_store.values() if task.status == status]

def is_serializable(payload):
    try:
        json.dumps(payload)
        return True
    except (TypeError, ValueError):
        return False

def create_task(task_type, payload, max_retries):
    if task_type not in vars(TaskTypes).values():
        raise ValueError(f"Invalid task type: {task_type}")
    
    if not is_serializable(payload):
        raise ValueError("Payload must be json serializable")
    
    if max_retries < 0:
        raise ValueError("Max Retries must be a non-negative integer")

    task = Task(task_type, payload, max_retries) 

    task_store[task.task_id] = task

    return task.task_id   

def mark_task_running(task_id):
    task = get_task(task_id)
    
    if task.status != Status.PENDING:
        return "ignore"
    
    task.status = Status.RUNNING
    task.updated_at = now()

    task_store[task_id] = task

def mark_task_completed(task_id):
    task = get_task(task_id)
    
    if task.status != Status.RUNNING:
        return "ignore"
    
    task.status = Status.COMPLETED
    task.updated_at = now()

    task_store[task_id] = task

def handle_task_failure(task_id, error_message):
    task = get_task(task_id)

    if task.status != Status.RUNNING:
        return "ignore"
    
    task.retry_count += 1
    task.last_error = error_message
    task.updated_at = now()

    if task.retry_count > task.max_retries:
        task.status = Status.DEAD
    else:
        task.status = Status.FAILED

    task_store[task_id] = task

def reset_task_for_retry(task_id):
    task = get_task(task_id)

    if task.status != Status.FAILED:
        return "ignore"
    
    task.status = Status.PENDING
    task.updated_at = now()

    task_store[task_id] = task
    