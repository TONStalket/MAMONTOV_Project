"""Pytest fixtures for the social network application."""

from collections.abc import Generator
from pathlib import Path
from typing import Any
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.dependencies import get_db  # noqa: E402  pylint: disable=wrong-import-position
from app.main import app  # noqa: E402  pylint: disable=wrong-import-position
from app import models  # noqa: E402  pylint: disable=wrong-import-position

TEST_DATABASE_URL = "sqlite:///./test_social.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

models.Base.metadata.create_all(bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
    # cleanup database between test sessions
    models.Base.metadata.drop_all(bind=test_engine)
    models.Base.metadata.create_all(bind=test_engine)


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def create_user(session: Session) -> Generator[dict[str, Any], None, None]:
    from app.security import get_password_hash  # noqa: E402  pylint: disable=wrong-import-position

    user_data = {
        "email": "user@example.com",
        "username": "testuser",
        "password": "strongpassword",
    }

    user = models.User(
        email=user_data["email"],
        username=user_data["username"],
        hashed_password=get_password_hash(user_data["password"]),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    yield {"instance": user, **user_data}

    session.query(models.User).delete()
    session.commit()
