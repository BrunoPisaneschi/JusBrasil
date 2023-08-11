from logging import basicConfig, getLogger, INFO
from re import search
from aiohttp import ClientSession
from api.exceptions import InvalidParameterError
from crawler.default.data_extractor import DataExtractor

# Configurando o log
basicConfig(filename='app.txt',
            level=INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


class FirstInstance:
    def __init__(self, codigo_tj, url_base):
        """
        Inicializa a classe FirstInstance.

        :param codigo_tj: Código de identificação do Tribunal de Justiça.
        :param url_base: URL base para as consultas HTTP.
        """
        self.url_base = url_base
        self.codigo_tj = codigo_tj

    async def capturar_dados(self, numero_processo):
        """
        Método público para iniciar a captura de dados da primeira instância.
        Realiza a busca, consulta, e extração dos dados relacionados ao número do processo fornecido.

        :param numero_processo: Número do processo a ser capturado.
        :return: Dados extraídos do processo.
        """
        logger.info("Iniciando captura dados primeira instancia")
        processo_codigo = await self._capturar_numero_processo_codigo(numero_processo=numero_processo)
        if not processo_codigo:
            logger.info("Número de processo não encontrado")
            return None
        html = await self._consultar_processo(processo_codigo=processo_codigo, numero_processo=numero_processo)
        logger.info("Extraindo dados primeira instancia")
        return self._extrair_dados(html=html)

    async def _capturar_numero_processo_codigo(self, numero_processo):
        """
        Método privado para capturar o código do processo com base no número fornecido.
        Divide o número do processo usando o código do TJ e realiza uma solicitação HTTP
        para obter o código do processo.

        :param numero_processo: Número do processo judicial a ser consultado.
        :return: Código do processo.
        :raises InvalidParameterError: Se o número do processo e o código da sigla do TJ não forem compatíveis.
        """
        try:
            numero_digito_ano_unificado, foro_numero_unificado = numero_processo.split(self.codigo_tj)
        except ValueError:
            logger.info("Erro na quebra do numero do processo")
            raise InvalidParameterError(
                message=f"Certifique-se de que o número do processo '{numero_processo}' e "
                        f"o código da sigla do TJ '{self.codigo_tj}' sejam compatíveis."
            )

        async with ClientSession() as client:
            response = await client.get(
                url=f"{self.url_base}/cpopg/search.do?"
                    f"conversationId=&"
                    f"cbPesquisa=NUMPROC&"
                    f"numeroDigitoAnoUnificado={numero_digito_ano_unificado[:-1]}&"
                    f"foro_numero_unificado={foro_numero_unificado[1:]}&"
                    f"dadosConsulta.valorConsultaNuUnificado={numero_processo}&"
                    f"dadosConsulta.valorConsultaNuUnificado=UNIFICADO&"
                    f"dadosConsulta.valorConsulta=&"
                    f"dadosConsulta.tipoNuProcesso=UNIFICADO",
                allow_redirects=False,
            )

            try:
                processo_codigo = search(r'(?<=processo.codigo=)(.*?)(?=&)', response.headers.get('location', "")).group()
            except AttributeError:
                text = await response.text()
                if 'Não existem informações disponíveis' in text:
                    return None
                else:
                    logger.error("Situação inesperada na execução")
                    return None

        return processo_codigo

    async def _consultar_processo(self, processo_codigo, numero_processo):
        """
        Método privado para realizar a consulta do processo usando o código do processo e número do processo.
        Realiza uma solicitação HTTP para obter os detalhes do processo.

        :param processo_codigo: Código do processo.
        :param numero_processo: Número do processo.
        :return: Conteúdo HTML da página do processo.
        """
        async with ClientSession() as client:
            response = await client.get(
                url=f"{self.url_base}/cpopg/show.do",
                params={
                    "processo.codigo": processo_codigo,
                    "processo.foro": "1",
                    "processo.numero": numero_processo
                }
            )
            return await response.text()

    @staticmethod
    def _extrair_dados(html):
        """
        Método privado para extrair os dados do conteúdo HTML fornecido.
        Utiliza a classe DataExtractor para extrair informações específicas.

        :param html: Conteúdo HTML da página do processo.
        :return: Dicionário contendo dados extraídos.
        """
        # Definindo os campos a serem extraídos
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

        # Utilizando o DataExtractor para fazer a extração
        extractor = DataExtractor(html)
        dados_extraidos = extractor.extract(fields_to_extract)

        return dados_extraidos
