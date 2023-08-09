from bs4 import BeautifulSoup


class DataExtractor:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

    def find_text(self, tag_id):
        try:
            return self.soup.find(id=tag_id).get_text(strip=True)
        except AttributeError:
            return None

    def find_table_data(self, table_id):
        table_data = []
        table = self.soup.find('table', {'id': table_id}) \
            if 'Partes' in table_id \
            else self.soup.find('tbody', {'id': table_id})

        if table:
            rows = table.find_all('tr')
            table_data = [
                self._capturar_texto_partes(row) if 'Partes' in table_id else self._capturar_movimentacoes(row)
                for row in rows
            ]

        if not table and 'tableTodasPartes' == table_id:
            return self.find_table_data(table_id="tablePartesPrincipais")
        elif not table and 'tabelaTodasMovimentacoes' == table_id:
            return self.find_table_data(table_id='tabelaUltimasMovimentacoes')

        return table_data

    @staticmethod
    def _capturar_texto_partes(row):
        tipo_parte = row.find('td', class_='label').get_text(strip=True)
        conteudo_parte = row.find('td', class_='nomeParteEAdvogado')
        nao_advogado = conteudo_parte.next.get_text(strip=True)
        advogados = {
            span.get_text(strip=True): span.next_sibling.get_text(strip=True)
            for span in conteudo_parte.find_all('span')
        }
        return {
            tipo_parte: nao_advogado,
            "Defesa": advogados
        }

    def _capturar_movimentacoes(self, row):
        try:
            data_movimentacao = row.find('td', class_='dataMovimentacao').get_text(strip=True)
        except AttributeError:
            data_movimentacao = row.find('td', class_='dataMovimentacaoProcesso').get_text(strip=True)

        movimentacao = row.find('td', class_='descricaoMovimentacao')

        if not movimentacao:
            movimentacao = row.find('td', class_='descricaoMovimentacaoProcesso')

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
        texto_movimentacao = movimentacao.get_text(strip=True, separator="|||")
        titulo_movimentacao, separador, descricao_movimentacao = texto_movimentacao.partition("|||")

        if separador:  # Se o separador estiver presente, o título e a descrição serão retornados.
            return titulo_movimentacao, descricao_movimentacao

        # Se o separador não estiver presente, o título completo será retornado, e a descrição será None.
        return titulo_movimentacao, None

    def extract(self, fields):
        return {
            field_name: self.find_text(tag_id) if tag_id not in ["tableTodasPartes", "tabelaTodasMovimentacoes"]
            else self.find_table_data(tag_id)
            for field_name, tag_id in fields.items()
        }