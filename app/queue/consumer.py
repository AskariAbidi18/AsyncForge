from app.redis_client import redis_client 

QUEUE_NAME = "asyncforge:tasks"

def get_next_task():
    print("[QUEUE] waiting for task...")

    result = redis_client.brpop(QUEUE_NAME)

    print("[QUEUE] redis returned:", result)

    if result:
        _, task_id = result
        return task_id

    return None
