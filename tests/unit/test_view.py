from unittest.mock import patch, AsyncMock
from uuid import uuid4
from json import dumps

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def solicitacao_id():
    return str(uuid4())


@pytest.fixture
def payload():
    return {
        "numero_processo": "12345",
        "sigla_tribunal": "TJ",
        "status": "Na Fila"
    }


@pytest.mark.asyncio
async def test_status_solicitacao_success(client, solicitacao_id, payload):
    with patch('database.service.set_data', new_callable=AsyncMock, return_value=None), \
            patch('main.get_data', new_callable=AsyncMock, return_value=dumps(payload).encode("utf-8")):
        response = client.get(f"/status-solicitacao/{solicitacao_id}")
        assert response.status_code == 200
        assert "numero_processo" in response.json()
        assert "sigla_tribunal" in response.json()
        assert "status" in response.json()


@pytest.mark.asyncio
async def test_status_solicitacao_not_found(client):
    with patch('database.service.get_data', new_callable=AsyncMock, return_value=None), \
            patch('main.get_data', new_callable=AsyncMock, return_value=None):
        response = client.get(f"/status-solicitacao/{str(uuid4())}")
        assert response.status_code == 404
