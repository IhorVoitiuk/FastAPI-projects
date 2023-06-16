import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This adds the parent directory of the current file to the Python path

import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
import pytest

from src.database.models import User
from src.repository.documents import get_user_by_email, update_documents_count


@pytest.fixture
def session():
    return MagicMock(spec=Session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="TestName",
        email="TestEmail@example.com",
        password="TestPassword",
        created_at=datetime.date(2023, 4, 20),
        avatar="http://avatars.example.com/profile/1",
        refresh_token="H#KL#@L@#H#KL#H@JK!JKL",
        confirmed=True,
    )


@pytest.mark.asyncio
async def test_get_user_by_email(session, user):
    email = "TestEmail@example.com"
    session.query().filter().first.return_value = user
    result = await get_user_by_email(email=email, db=session)
    assert result.email == email


@pytest.mark.asyncio
async def test_update_documents_count(session, user):
    email = "TestEmail@example.com"
    session.query().filter().first.return_value = user
    document_count = await update_documents_count(email, 2, db=session)
    assert document_count == 2


if __name__ == "__main__":
    pytest.main()
