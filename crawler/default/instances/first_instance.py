from logging import basicConfig, getLogger, INFO

from re import search

from httpx import AsyncClient

from api.exceptions import InvalidParameterError
from crawler.default.data_extractor import DataExtractor

# Configurando o log
basicConfig(filename='app.txt', 
            level=INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


class FirstInstance:
    def __init__(self, codigo_tj, url_base):
        self.url_base = url_base
        self.codigo_tj = codigo_tj

    async def capturar_dados(self, numero_processo):
        logger.info("Iniciando captura dados primeira instancia")
        processo_codigo = await self._capturar_numero_processo_codigo(numero_processo=numero_processo)
        if not processo_codigo:
            logger.info("Número de processo não encontrado")
        html = await self._consultar_processo(processo_codigo=processo_codigo, numero_processo=numero_processo)
        logger.info("Extraindo dados primeira instancia")
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
