import uuid

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime
)

from sqlalchemy.dialects.postgresql import UUID, JSONB

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.constants import Status
from app.utils.time import now

from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    task_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    ) 

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=Status.PENDING,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        nullable = False,
        default = 0,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable = True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable=False,
        default = now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable=False,
        default = now,
        onupdate = now,
    )
    