from re import search

from httpx import AsyncClient

from api.exceptions import InvalidParameterError
from crawler.default.data_extractor import DataExtractor


class SecondInstance:
    def __init__(self, codigo_tj, url_base):
        self.url_base = url_base
        self.codigo_tj = codigo_tj

    async def capturar_dados(self, numero_processo):
        processo_codigo = await self._capturar_numero_processo_codigo(numero_processo=numero_processo)
        if not processo_codigo:
            return None
        html = await self._consultar_processo(processo_codigo=processo_codigo)
        return self._extrair_dados(html=html)

    async def _capturar_numero_processo_codigo(self, numero_processo):
        try:
            numero_digito_ano_unificado, foro_numero_unificado = numero_processo.split(self.codigo_tj)
        except ValueError:
            raise InvalidParameterError(
                message=f"Certifique-se de que o número do processo '{numero_processo}' e "
                        f"o código da sigla do TJ '{self.codigo_tj}' sejam compatíveis."
            )

        async with AsyncClient() as client:
            response = await client.get(
                url=f"{self.url_base}/cposg5/search.do?"
                    f"conversationId=&"
                    f"paginaConsulta=0&"
                    f"cbPesquisa=NUMPROC&"
                    f"numeroDigitoAnoUnificado={numero_digito_ano_unificado[:-1]}&"
                    f"foroNumeroUnificado={foro_numero_unificado[1:]}&"
                    f"dePesquisaNuUnificado={numero_processo}&"
                    f"dePesquisaNuUnificado=UNIFICADO&"
                    f"dePesquisa=&"
                    f"tipoNuProcesso=UNIFICADO"
            )

            try:
                processo_codigo = search(r'(?<=id=\"processoSelecionado\"\svalue=\")(.*?)(?=")', response.text).group()
            except AttributeError:
                if 'Não existem informações disponíveis' in response.text:
                    return None
                else:
                    return None

        return processo_codigo

    async def _consultar_processo(self, processo_codigo):
        async with AsyncClient() as client:
            response = await client.get(
                url=f"{self.url_base}/cposg5/show.do",
                params={
                    "processo.codigo": processo_codigo,
                }
            )
            return response.content

    @staticmethod
    def _extrair_dados(html):
        fields_to_extract = {
            "classe": "classeProcesso",
            "area": "areaProcesso",
            "assunto": "assuntoProcesso",
            "data_distribuicao": "dataHoraDistribuicaoProcesso",
            "juiz": "juizProcesso",
            "valor_acao": "valorAcaoProcesso",
            "partes_processo": "tableTodasPartes",
            "lista_movimentacoes": "tabelaTodasMovimentacoes"
        }

        extractor = DataExtractor(html)
        dados_extraidos = extractor.extract(fields_to_extract)

        return dados_extraidos
