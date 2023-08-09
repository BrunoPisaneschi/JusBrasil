from re import search

from httpx import AsyncClient
from decouple import config

from crawler.tjal.data_extractor import DataExtractor


class TJAL:
    def __init__(self):
        self.url_base = config("URL_BASE_TJAL")
        self.codigo_tj = "8.02"

    async def capturar_dados(self, numero_processo):
        processo_codigo = await self._capturar_numero_processo_codigo(numero_processo=numero_processo)
        html = await self._consultar_processo(processo_codigo=processo_codigo, numero_processo=numero_processo)
        return self._extrair_dados(html=html)

    async def _capturar_numero_processo_codigo(self, numero_processo):
        numero_digito_ano_unificado, foro_numero_unificado = numero_processo.split(self.codigo_tj)

        async with AsyncClient() as client:
            response = await client.get(
                url=f"{self.url_base}/cpopg/search.do?"
                    f"conversationId=&"
                    f"cbPesquisa=NUMPROC&"
                    f"numeroDigitoAnoUnificado={numero_digito_ano_unificado[:-1]}&"
                    f"foroNumeroUnificado={foro_numero_unificado[1:]}&"
                    f"dadosConsulta.valorConsultaNuUnificado={numero_processo}&"
                    f"dadosConsulta.valorConsultaNuUnificado=UNIFICADO&"
                    f"dadosConsulta.valorConsulta=&"
                    f"dadosConsulta.tipoNuProcesso=UNIFICADO",
                follow_redirects=False,
            )

            processo_codigo = search(r'(?<=processo.codigo=)(.*?)(?=&)', response.headers.get('location', "")).group()
            return processo_codigo

    async def _consultar_processo(self, processo_codigo, numero_processo):
        async with AsyncClient() as client:
            response = await client.get(
                url=f"{self.url_base}/cpopg/show.do",
                params={
                    "processo.codigo": processo_codigo,
                    "processo.foro": "1",
                    "processo.numero": numero_processo
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
