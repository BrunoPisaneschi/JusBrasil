import pytest
from unittest.mock import AsyncMock, patch
from api.exceptions import InvalidParameterError
from crawler.default.instances.second_instance import SecondInstance

# Mock para a resposta do ClientSession
mock_response = AsyncMock()
mock_response.text.return_value = 'Sample Text'


@pytest.mark.asyncio
async def test_capturar_numero_processo_codigo_invalid():
    instance = SecondInstance("TJ", "http://example.com")

    with pytest.raises(InvalidParameterError):
        await instance._capturar_numero_processo_codigo("123456")


@pytest.mark.asyncio
@patch('crawler.default.instances.second_instance.ClientSession')
async def test_consultar_processo(mock_session):
    mock_session.return_value.__aenter__.return_value.get.return_value = mock_response

    instance = SecondInstance("TJ", "http://example.com")

    result = await instance._consultar_processo("789")

    assert result == "Sample Text"
