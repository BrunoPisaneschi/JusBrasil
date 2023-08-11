import pytest
from api.exceptions import InvalidParameterError
from api.schemas.input import ConsultaProcessoInput, StatusSolicitacaoInput


# Testes para o modelo ConsultaProcessoInput

def test_valid_numero_processo():
    input_data = {
        "numero_processo": "1234567-89.2023.8.01.2345",
        "sigla_tribunal": "TJAL"
    }
    consulta = ConsultaProcessoInput(**input_data)
    assert consulta.numero_processo == input_data["numero_processo"]


def test_invalid_numero_processo():
    input_data = {
        "numero_processo": "1234567-89.20238.01.2345",
        "sigla_tribunal": "TJAL"
    }
    with pytest.raises(InvalidParameterError) as exc:
        ConsultaProcessoInput(**input_data)
    assert "não é compatível com o padrão" in str(exc.value)


def test_valid_sigla_tribunal():
    input_data = {
        "numero_processo": "1234567-89.2023.8.01.2345",
        "sigla_tribunal": "TJCE"
    }
    consulta = ConsultaProcessoInput(**input_data)
    assert consulta.sigla_tribunal == input_data["sigla_tribunal"]


# Para este teste, assumimos que a sigla "TJBR" não está na lista de tribunais disponíveis.
def test_invalid_sigla_tribunal():
    input_data = {
        "numero_processo": "1234567-89.2023.8.01.2345",
        "sigla_tribunal": "TJBR"
    }
    with pytest.raises(ValueError):
        ConsultaProcessoInput(**input_data)


# Testes para o modelo StatusSolicitacaoInput

def test_valid_numero_solicitacao():
    input_data = {
        "numero_solicitacao": "550e8400-e29b-41d4-a716-446655440000"
    }
    status = StatusSolicitacaoInput(**input_data)
    assert status.numero_solicitacao == input_data["numero_solicitacao"]


def test_invalid_numero_solicitacao():
    input_data = {
        "numero_solicitacao": "12345"
    }
    with pytest.raises(InvalidParameterError) as exc:
        StatusSolicitacaoInput(**input_data)
    assert "não é compatível com o formato UUID" in str(exc.value)
