from fastapi import status
from src.conf import messages

from src.database.db import get_db


def test_healthchecker_success(client):
    response = client.get("/api/healthchecker")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"message": messages.HEALTHCHECKER_MESSAGE}
