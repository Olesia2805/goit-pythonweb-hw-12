from fastapi import status
from unittest.mock import Mock, MagicMock
from src.conf import messages


def test_healthchecker_success(client):
    response = client.get("/api/healthchecker")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"message": messages.HEALTHCHECKER_MESSAGE}
