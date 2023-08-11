import pytest
from unittest.mock import patch, AsyncMock
from crawler.default.instances.first_instance import FirstInstance


@pytest.mark.asyncio
async def test_capturar_dados_success():
    instance = FirstInstance(codigo_tj="TJ", url_base="http://example.com")

    with patch("crawler.default.data_extractor.DataExtractor.extract", return_value={"classe": "Teste"}), \
         patch("crawler.default.instances.first_instance.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.headers = {'location': 'some_location?processo.codigo=123&'}
        mock_response.text.return_value = 'Sample Text'
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await instance.capturar_dados(numero_processo="123TJ456")

        assert result == {"classe": "Teste"}
