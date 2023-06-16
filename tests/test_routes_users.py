import pytest
from unittest.mock import MagicMock, patch

from src.database.models import User
from src.routes.users import cloudinary


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    get_current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    get_current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["access_token"]


def test_read_users_me(client, token, user):
    response = client.get("api/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200, response.text
    data = response.json()
    assert data.get("username") == user.get("username")
    assert data.get("email") == user.get("email")
