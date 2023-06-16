from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from src.routes.documents import router
from src.database.models import User
from src.database.db import get_db
from src.services.auth import auth_service
from src.services.documents import pdf_utils

client = TestClient(router)


def test_convert_images_to_pdf_route(monkeypatch):
    # Mock dependencies
    mock_pdf_utils = MagicMock()
    monkeypatch.setattr("src.routes.documents.pdf_utils", mock_pdf_utils)

    mock_update_documents_count = MagicMock()
    monkeypatch.setattr(
        "src.repository.documents.update_documents_count",
        mock_update_documents_count,
    )

    files = [
        ("file", ("image1.jpg", b"image1 content", "image/jpeg")),
        ("file", ("image2.jpg", b"image2 content", "image/jpeg")),
    ]
    user = User(email="test@example.com")

    pdf_data = b"pdf data"
    mock_pdf_utils.convert_images_to_pdf.return_value = pdf_data

    total_count = 5
    mock_update_documents_count.return_value = total_count

    response = client.post(
        "/api/documents/convert_images_to_pdf",
        files=files,
        headers={"Authorization": "Bearer <access_token>"},
    )

    assert response.status_code == 404

    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
