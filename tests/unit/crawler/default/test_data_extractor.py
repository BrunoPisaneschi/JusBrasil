from unittest.mock import patch, Mock

from crawler.default.data_extractor import DataExtractor

html_sample = """
<html>
    <body>
        <p id="sample_id">Sample Text</p>
        <table id="tablePartesPrincipais">
            <tr>
                <td class="label">Reclamante</td>
                <td class="nomeParteEAdvogado">João Silva <span>Advogado:</span> Dr. José</td>
            </tr>
        </table>
        <tbody id="tabelaUltimasMovimentacoes">
            <tr>
                <td class="dataMovimentacao">01/01/2022</td>
                <td class="descricaoMovimentacao">Titulo Movimentação|||Descrição detalhada da movimentação</td>
            </tr>
        </tbody>
    </body>
</html>
"""


def test_extract_with_mock():
    # Instanciação do objeto e definição do mock
    extractor = DataExtractor(html_sample)

    # Criando um mock para o método find_text
    mock_find_text = Mock(return_value="Mocked Text")

    with patch.object(extractor, 'find_text', mock_find_text):
        fields = {"Texto": "sample_id"}
        extracted_data = extractor.extract(fields)

        # Afirmar que o método mockado foi chamado com o argumento correto
        mock_find_text.assert_called_once_with("sample_id")

        # Afirmar que o resultado é o esperado
        assert extracted_data == {"Texto": "Mocked Text"}


def test_find_text_attribute_error():
    # Instanciação do objeto
    extractor = DataExtractor(html_sample)

    # Testando a exceção AttributeError no método find_text
    with patch.object(extractor.soup, 'find', side_effect=AttributeError):
        result = extractor.find_text("invalid_id")
        assert result is None


def test_find_text_with_mock():
    extractor = DataExtractor(html_sample)

    # Criando um mock para o método find_text
    mock_find_text = Mock(return_value="Mocked Text")

    with patch.object(extractor, 'find_text', mock_find_text):
        result = extractor.find_text("sample_id")
        mock_find_text.assert_called_once_with("sample_id")
        assert result == "Mocked Text"


def test_find_table_data_with_mock():
    extractor = DataExtractor(html_sample)

    # Criando mocks para os métodos internos.
    mock_capturar_texto_partes = Mock(return_value={
        "Reclamante": "John Mocked Doe",
        "Defesa": {}
    })

    mock_capturar_movimentacoes = Mock(return_value={
        "Data": "01/01/2023",
        "Movimento": {
            "titulo_movimentacao": "Movimento Mocked 1",
            "descricao_movimentacao": "Descrição Mocked 1"
        }
    })

    with patch.object(extractor, '_capturar_texto_partes', mock_capturar_texto_partes), \
            patch.object(extractor, '_capturar_movimentacoes', mock_capturar_movimentacoes):
        # Testando o método find_table_data para partes.
        table_data_partes = extractor.find_table_data("tableTodasPartes")

        mock_capturar_texto_partes.assert_called_once()

        expected_data_partes = [{
            "Reclamante": "John Mocked Doe",
            "Defesa": {}
        }]

        assert table_data_partes == expected_data_partes

        # Testando o método find_table_data para movimentações.
        table_data_movimentacoes = extractor.find_table_data("tabelaTodasMovimentacoes")

        mock_capturar_movimentacoes.assert_called_once()

        expected_data_movimentacoes = [{
            "Data": "01/01/2023",
            "Movimento": {
                "titulo_movimentacao": "Movimento Mocked 1",
                "descricao_movimentacao": "Descrição Mocked 1"
            }
        }]

        assert table_data_movimentacoes == expected_data_movimentacoes
