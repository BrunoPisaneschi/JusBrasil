from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pytest import raises

from pydantic import ValidationError

from api.exceptions import InvalidParameterError
from api.schemas.output import (
    ConsultaProcessoOutput,
    ExtractDataOutput,
    ExtractDataSecondInstanceOutput,
    StatusSolicitacaoOutput
)


def test_valida_numero_solicitacao_valid():
    """Testa se a validação do UUID é bem-sucedida com um UUID válido."""
    valid_uuid = str(uuid4())
    ConsultaProcessoOutput(numero_solicitacao=valid_uuid)


@pytest.mark.parametrize("invalid_uuid", ["invalid_uuid_string"])
def test_valida_numero_solicitacao_invalid(invalid_uuid):
    """Testa se a validação do UUID falha com uma string inválida."""
    with MagicMock(side_effect=InvalidParameterError("Mocked error")):
        with raises(InvalidParameterError):
            ConsultaProcessoOutput(numero_solicitacao=invalid_uuid)


def test_valid_extract_data():
    """Testa se o modelo é válido com dados corretos."""
    valid_data = {
        'classe': 'Penal',
        'area': 'Criminal',
        'assunto': 'Roubo',
        'data_distribuicao': 'Sorteio',
        'juiz': 'Dr. João Silva',
        'valor_acao': '5000,00',
        'partes_processo': [],
        'lista_movimentacoes': []
    }
    ExtractDataOutput(**valid_data)


def test_valid_output():
    """Testa um output válido para ExtractDataSecondInstanceOutput."""
    valid_data = {
        "classe": "Recurso Penal",
        "area": "Criminal",
        "assunto": "Furto",
        "partes_processo": [],
        "lista_movimentacoes": []
    }
    output = ExtractDataSecondInstanceOutput(**valid_data)
    assert output.classe == "Recurso Penal"
    assert output.area == "Criminal"


def test_missing_required_field():
    """Testa a ausência de campos obrigatórios para ExtractDataSecondInstanceOutput."""
    invalid_data = {
        "classe": "Recurso Penal",
        "assunto": "Furto",
        "partes_processo": [],
        "lista_movimentacoes": []
    }
    with raises(ValidationError):
        ExtractDataSecondInstanceOutput(**invalid_data)


def test_valid_output_first_instance_only():
    """Testa um output válido para StatusSolicitacaoOutput com apenas dados da primeira instância."""
    valid_data = {
        "numero_processo": "0113546-72.2018.8.02.0001",
        "sigla_tribunal": "TJAL",
        "status": "Na Fila",
        "first_instance": {
            "classe": "Penal",
            "area": "Criminal",
            "assunto": "Roubo",
            "data_distribuicao": "Sorteio",
            "juiz": "Dr. João Silva",
            "partes_processo": [],
            "lista_movimentacoes": []
        }
    }
    output = StatusSolicitacaoOutput(**valid_data)
    assert output.numero_processo == "0113546-72.2018.8.02.0001"
    assert output.first_instance.classe == "Penal"


def test_valid_output_both_instances():
    """Testa um output válido para StatusSolicitacaoOutput com dados de ambas as instâncias."""
    valid_data = {
        "numero_processo": "0113546-72.2018.8.02.0001",
        "sigla_tribunal": "TJAL",
        "status": "Na Fila",
        "first_instance": ExtractDataOutput(
            classe="Penal",
            area="Criminal",
            assunto="Roubo",
            data_distribuicao="Sorteio",
            juiz="Dr. João Silva",
            valor_acao="5000,00",
            partes_processo=[],
            lista_movimentacoes=[]
        ),
        "second_instance": ExtractDataSecondInstanceOutput(
            classe="Recurso Penal",
            area="Criminal",
            assunto="Furto",
            valor_acao="2500,55",
            partes_processo=[],
            lista_movimentacoes=[]
        )
    }

    output = StatusSolicitacaoOutput(**valid_data)

    assert output.numero_processo == "0113546-72.2018.8.02.0001"
    assert output.sigla_tribunal == "TJAL"
    assert output.status == "Na Fila"
    assert isinstance(output.first_instance, ExtractDataOutput)
    assert isinstance(output.second_instance, ExtractDataSecondInstanceOutput)


def test_invalid_output():
    """Testa um output inválido para StatusSolicitacaoOutput."""
    invalid_data = {
        "numero_processo": 123456  # Um número em vez de uma string
    }
    with raises(ValidationError):
        StatusSolicitacaoOutput(**invalid_data)
