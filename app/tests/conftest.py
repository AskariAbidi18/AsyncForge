import os

os.environ["ENV_FILE"] = ".env.test"

import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from unittest.mock import patch


@pytest.fixture(scope="function")
def db():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    try:
        yield session

    finally:
        session.close()

        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):

    from app.database import get_db

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_enqueue():

    with patch("app.services.task_service.enqueue_task"):
        yield
