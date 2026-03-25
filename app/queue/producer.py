from app.redis_client import redis_client

QUEUE_NAME = "asyncforge:tasks"

def enqueue_task(task_id):
    print(f"[QUEUE] pushing task {task_id}")
    redis_client.lpush(QUEUE_NAME, str(task_id))
   