import pytest

from unittest.mock import MagicMock, patch

from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def access_token(client, user, session, monkeypatch):
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


def test_create_contacts(client, access_token):
    with patch.object(auth_service, "redis") as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/contacts",
            json={
                "first_name": "Dima",
                "last_name": "Grench",
                "email": "example@gmail.com",
                "phone_number": "+380735637891",
                "birthday": "2000-04-28",
                "description": "Hello World!",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["email"] == "example@gmail.com"
        assert "id" in data


def test_get_contact(client, access_token):
    with patch.object(auth_service, "redis") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == 1
        assert data["first_name"] == "Dima"
        assert data["last_name"] == "Grench"
        assert data["email"] == "example@gmail.com"
        assert data["phone_number"] == "+380735637891"
        assert data["birthday"] == "2000-04-28"
        assert data["description"] == "Hello World!"


def test_get_contacts(client, access_token):
    with patch.object(auth_service, "redis") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "example@gmail.com"
        assert "id" in data


def test_export_contacts_to_json(client, access_token):
    with patch.object(auth_service, "redis") as r_mock:
        r_mock.get.return_value = None

        response = client.get(
            "/api/export",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"format": "json", "limit": 100, "offset": 0},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        result = response.json()
        assert "export_contacts" in result
        assert "content_type" in result["export_contacts"]
        assert "file_extension" in result["export_contacts"]
        assert "exported_data" in result["export_contacts"]

        exported_data = result["export_contacts"]["exported_data"]
        assert exported_data["id"] == 1
        assert exported_data["first_name"] == "Dima"
        assert exported_data["last_name"] == "Grench"
        assert exported_data["email"] == "example@gmail.com"
        assert exported_data["phone_number"] == "+380735637891"
        assert exported_data["birthday"] == "2000-04-28"
        assert exported_data["description"] == "Hello World!"

        # Test with unsupported format
        response = client.get(
            "/api/export",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"format": "xml", "limit": 100, "offset": 0},
        )

        assert response.status_code == 415
        assert response.json()["detail"] == "Unsupported format"


def test_export_contacts_to_csv(client, access_token):
    with patch.object(auth_service, "redis") as r_mock:
        r_mock.get.return_value = None

        response = client.get(
            "/api/export",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"format": "csv", "limit": 100, "offset": 0},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv"

        # Add your assertions for the CSV content if necessary

        # Test with unsupported format
        response = client.get(
            "/api/export",
            headers={"Authorization": "Bearer your_access_token"},
            params={"format": "xml", "limit": 100, "offset": 0},
        )

        assert response.status_code == 415
        assert response.json()["detail"] == "Unsupported format"
