from json import dumps, JSONDecodeError

import pytest
from unittest.mock import MagicMock, patch, AsyncMock, call

from api.services.process_handler import process_request


@pytest.mark.asyncio
async def test_process_request():
    # Mock RedisConnection
    mock_redis = MagicMock()
    mock_redis.get_data.return_value = '{"numero_processo": "1234", "sigla_tribunal": "TJAL"}'

    # Mocking import_module
    mock_tjal_instance = MagicMock()
    mock_tjal_instance.capturar_dados = AsyncMock(return_value={"some_data": "value"})
    mock_module = MagicMock()
    mock_module.TJAL.return_value = mock_tjal_instance

    mock_model_validate = MagicMock()

    mock_model_validate.model_dump.side_effect = {"some_data": "value", "another_key": "another_value"}

    mock_output = MagicMock()
    mock_output.model_validate.return_value = mock_model_validate

    with patch('api.services.process_handler.RedisConnection', return_value=mock_redis), \
            patch('api.services.process_handler.import_module', return_value=mock_module), \
            patch('api.schemas.output.StatusSolicitacaoOutput', return_value=mock_output):
        await process_request("test_solicitacao_id")


@pytest.mark.asyncio
async def test_process_request_redis_failure():
    # Mock RedisConnection para simular uma falha
    mock_redis = MagicMock()
    mock_redis.get_data.side_effect = Exception("Redis error")

    with patch('api.services.process_handler.RedisConnection', return_value=mock_redis):
        with pytest.raises(Exception, match="Redis error"):
            await process_request("test_solicitacao_id")


@pytest.mark.asyncio
async def test_process_request_import_failure():
    mock_redis = MagicMock()
    mock_redis.get_data.return_value = '{"numero_processo": "1234", "sigla_tribunal": "UNKNOWN"}'

    # Retornar None para simular falha na importação do módulo
    with patch('api.services.process_handler.RedisConnection', return_value=mock_redis), \
            patch('api.services.process_handler.import_module', return_value=None):
        # Não esperamos mais uma exceção aqui porque a função foi modificada para lidar com ela
        await process_request("test_solicitacao_id")

        # Verificar as chamadas ao método set_data do mock_redis
        calls = [call(key="test_solicitacao_id",
                      value=dumps({
                          "numero_processo": "1234",
                          "sigla_tribunal": "UNKNOWN",
                          "status": "Em processamento"})),
                 call(key="test_solicitacao_id",
                      value=dumps({
                          "numero_processo": "1234",
                          "sigla_tribunal": "UNKNOWN",
                          "status": "Erro tribunal inexistente"}))]

        mock_redis.set_data.assert_has_calls(calls)


@pytest.mark.asyncio
async def test_solicitacao_com_dados_invalidos_no_redis():
    # Dados inválidos no Redis
    mock_redis = MagicMock()
    mock_redis.get_data.return_value = 'Dados inválidos'

    with patch('api.services.process_handler.RedisConnection', return_value=mock_redis):
        with pytest.raises(JSONDecodeError, match=r"Expecting value: line 1 column 1 \(char 0\)"):
            await process_request("id_solicitacao_teste")
