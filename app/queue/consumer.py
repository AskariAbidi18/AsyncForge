from app.redis_client import redis_client 

QUEUE_NAME = "asyncforge:tasks"

def get_next_task():
    result = redis_client.brpop(QUEUE_NAME)

    if result:
        _, task_id = result
        return task_id
    
    return None 
