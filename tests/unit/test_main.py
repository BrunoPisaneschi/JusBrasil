import json
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_handle_invalid_parameter_error():
    response = client.post("/consulta-processo", json={"numero_processo": "123", "sigla_tribunal": "TJAL"})
    assert response.status_code == 422  # Expected status code for InvalidParameterError
    assert {
               'message': "numero_processo '123' não é compatível com o padrão NNNNNNN-DD.AAAA.J.TR.OOOO"} == response.json()


@patch("main.redis.get_data",
       Mock(return_value='{"numero_processo": "12345", "sigla_tribunal": "TJSP", "status": "Na Fila"}'))
def test_status_solicitacao():
    response = client.get("/status-solicitacao/d00bc000-0f0d-0d00-0cdf-000b00d00000")
    assert response.status_code == 200
    assert json.loads(response.content) == {
        "numero_processo": "12345",
        "sigla_tribunal": "TJSP",
        "status": "Na Fila"
    }


@patch("main.redis.get_data", Mock(return_value=None))
def test_status_solicitacao_not_found():
    response = client.get("/status-solicitacao/d00bc000-0f0d-0d00-0cdf-000b00d00000")
    assert response.status_code == 404
    assert json.loads(response.content) == {"error": "Solicitação não encontrada"}
