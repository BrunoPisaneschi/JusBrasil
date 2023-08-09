from bs4 import BeautifulSoup


class DataExtractor:
    """
    Classe DataExtractor responsável por extrair informações específicas de um HTML.

    :param html: String HTML da qual os dados serão extraídos.
    """

    def __init__(self, html):
        """
        Inicializa o objeto BeautifulSoup, que será usado para a extração de dados.

        :param html: String HTML da qual os dados serão extraídos.
        """
        self.soup = BeautifulSoup(html, 'html.parser')

    def find_text(self, tag_id):
        """
        Encontra e retorna o texto de uma tag com o ID fornecido.

        :param tag_id: ID da tag HTML.
        :return: Texto encontrado ou None se a tag não for encontrada.
        """
        try:
            return self.soup.find(id=tag_id).get_text(strip=True)
        except AttributeError:
            return None

    def find_table_data(self, table_id):
        """
        Encontra e retorna os dados de uma tabela com o ID fornecido.

        :param table_id: ID da tabela HTML.
        :return: Dados da tabela encontrada ou redireciona para outra tabela dependendo da ID.
        """
        # Inicializa a lista que conterá os dados da tabela.
        table_data = []

        # Procura a tabela pelo ID especificado, com lógica específica se o 'Partes' estiver presente no ID.
        table = self.soup.find('table', {'id': table_id}) \
            if 'Partes' in table_id \
            else self.soup.find('tbody', {'id': table_id})

        # Se a tabela for encontrada, processa as linhas.
        if table:
            rows = table.find_all('tr')
            table_data = [
                self._capturar_texto_partes(row) if 'Partes' in table_id else self._capturar_movimentacoes(row)
                for row in rows
            ]

        # Se a tabela não for encontrada, redireciona para outra tabela com base no ID.
        if not table and 'tableTodasPartes' == table_id:
            return self.find_table_data(table_id="tablePartesPrincipais")
        elif not table and 'tabelaTodasMovimentacoes' == table_id:
            return self.find_table_data(table_id='tabelaUltimasMovimentacoes')

        return table_data

    @staticmethod
    def _capturar_texto_partes(row):
        """
        Captura informações de texto de partes a partir de uma linha de tabela.

        :param row: Objeto BeautifulSoup representando uma linha de tabela.
        :return: Dicionário contendo informações sobre o tipo de parte, o nome da parte (se não for um advogado)
                 e a defesa (se for um advogado).
        """
        # Encontra o tipo da parte (por exemplo, Reclamante, Reclamado) na célula com a classe 'label'.
        tipo_parte = row.find('td', class_='label').get_text(strip=True)

        # Encontra o conteúdo da parte na célula com a classe 'nomeParteEAdvogado'.
        conteudo_parte = row.find('td', class_='nomeParteEAdvogado')

        # Se a parte não for um advogado, captura o nome diretamente.
        nao_advogado = conteudo_parte.next.get_text(strip=True)

        # Se a parte for um advogado, captura os detalhes do advogado, como nome e inscrição.
        advogados = {
            span.get_text(strip=True): span.next_sibling.get_text(strip=True)
            for span in conteudo_parte.find_all('span')
        }

        # Retorna um dicionário contendo o tipo da parte, o nome da parte (se não for um advogado)
        # e a defesa (se for um advogado).
        return {
            tipo_parte: nao_advogado,
            "Defesa": advogados
        }

    def _capturar_movimentacoes(self, row):
        """
        Captura informações de movimentações a partir de uma linha de tabela.

        :param row: Objeto BeautifulSoup representando uma linha de tabela.
        :return: Dicionário contendo informações sobre a movimentação.
        """
        # Tenta encontrar a data da movimentação.
        try:
            data_movimentacao = row.find('td', class_='dataMovimentacao').get_text(strip=True)
        except AttributeError:
            data_movimentacao = row.find('td', class_='dataMovimentacaoProcesso').get_text(strip=True)

        # Encontra a célula da tabela que contém os detalhes da movimentação.
        movimentacao = row.find('td', class_='descricaoMovimentacao')
        if not movimentacao:
            movimentacao = row.find('td', class_='descricaoMovimentacaoProcesso')

        # Extrai o título e a descrição da movimentação.
        titulo_movimentacao, descricao_movimentacao = self._capturar_dados_movimentacoes(movimentacao)

        return {
            "Data": data_movimentacao,
            "Movimento": {
                "titulo_movimentacao": titulo_movimentacao,
                "descricao_movimentacao": descricao_movimentacao
            }
        }

    @staticmethod
    def _capturar_dados_movimentacoes(movimentacao):
        """
        Captura detalhes das movimentações, como título e descrição.

        :param movimentacao: Objeto BeautifulSoup representando a célula da tabela com os dados de movimentação.
        :return: Título e descrição da movimentação.
        """
        # Extrai o texto da célula, usando "|||" como separador.
        texto_movimentacao = movimentacao.get_text(strip=True, separator="|||")

        # Divide o texto em título e descrição usando o separador.
        titulo_movimentacao, separador, descricao_movimentacao = texto_movimentacao.partition("|||")

        # Se o separador estiver presente, o título e a descrição serão retornados.
        # Caso contrário, retorna o título completo e None para a descrição.
        if separador:
            return titulo_movimentacao, descricao_movimentacao
        return titulo_movimentacao, None

    def extract(self, fields):
        """
        Extrai os dados especificados dos campos fornecidos e retorna como um dicionário.

        :param fields: Dicionário contendo os nomes dos campos e os IDs de tag correspondentes.
        :return: Dicionário contendo os dados extraídos.
        """
        return {
            field_name: self.find_text(tag_id) if tag_id not in ["tableTodasPartes", "tabelaTodasMovimentacoes"]
            else self.find_table_data(tag_id)
            for field_name, tag_id in fields.items()
        }
