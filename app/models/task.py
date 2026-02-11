from app.utils.time import now
from app.utils.constants import Status
import uuid

class Task:
    def __init__(self, task_type, payload, max_retries):
        self.task_id = uuid.uuid4() 
        self.task_type = task_type
        self.payload = payload
        self.max_retries = max_retries
        self.status = Status.PENDING
        self.retry_count = 0
        self.last_error = None
        self.created_at = now()
        self.updated_at = now()

