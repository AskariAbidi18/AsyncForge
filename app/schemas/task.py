from datetime import datetime

from pydantic import BaseModel, ConfigDict

import uuid


class CreateTaskRequest(BaseModel):
    task_type: str
    payload: dict
    max_retries: int


class TaskResponse(BaseModel):
    task_id: str
    task_type: str
    payload: dict
    status: str
    retry_count: int
    max_retries: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskCreatedResponse(BaseModel):
    task_id : uuid.UUID
