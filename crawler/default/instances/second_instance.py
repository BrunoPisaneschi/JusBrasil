from logging import basicConfig, getLogger, INFO

from re import search

from aiohttp import ClientSession

from api.exceptions import InvalidParameterError
from crawler.default.data_extractor import DataExtractor

# Configurando o log básico com detalhes como nome do arquivo, nível e formato.
basicConfig(filename='app.txt',
            level=INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


class SecondInstance:
    def __init__(self, codigo_tj, url_base):
        """
        Inicializa a classe SecondInstance para extrair dados de uma segunda instância judicial.

        :param codigo_tj: Código da instância judicial.
        :param url_base: URL base para a consulta do processo.
        """
        self.url_base = url_base
        self.codigo_tj = codigo_tj

    async def capturar_dados(self, numero_processo):
        """
        Inicia o processo de captura de dados da segunda instância.

        :param numero_processo: Número do processo judicial a ser consultado.
        :return: Dicionário contendo os dados extraídos ou None se as informações não estiverem disponíveis.
        """
        # Log da iniciação da captura dos dados.
        logger.info("Iniciando captura dados segunda instancia")

        # Captura o código do processo.
        processo_codigo = await self._capturar_numero_processo_codigo(numero_processo=numero_processo)

        # Se o código do processo não for encontrado, registra uma mensagem e retorna None.
        if not processo_codigo:
            logger.info("Não existem informações em segunda instância para esse processo")
            return None

        # Consulta os detalhes do processo usando o código capturado.
        html = await self._consultar_processo(processo_codigo=processo_codigo)

        # Log da extração dos dados.
        logger.info("Extraindo dados segunda instancia")

        # Extração dos dados e retorno.
        return self._extrair_dados(html=html)

    async def _capturar_numero_processo_codigo(self, numero_processo):
        """
        Método privado para capturar o código do processo com base no número fornecido.
        Divide o número do processo usando o código do TJ e realiza uma solicitação HTTP
        para obter o código do processo.

        :param numero_processo: Número do processo judicial a ser consultado.
        :return: Código do processo ou None se as informações não estiverem disponíveis.
        :raises InvalidParameterError: Se o número do processo e o código da sigla do TJ não forem compatíveis.
        """
        try:
            numero_digito_ano_unificado, foro_numero_unificado = numero_processo.split(self.codigo_tj)
        except ValueError:
            raise InvalidParameterError(
                message=f"Certifique-se de que o número do processo '{numero_processo}' e "
                        f"o código da sigla do TJ '{self.codigo_tj}' sejam compatíveis."
            )

        # Criando um cliente assíncrono para fazer a requisição HTTP.
        async with ClientSession() as client:
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
            html = await response.text()
            # Usando expressão regular para extrair o código do processo.
            try:
                processo_codigo = search(r'(?<=id=\"processoSelecionado\"\svalue=\")(.*?)(?=")', html).group()
            except AttributeError:
                if 'Não existem informações disponíveis' in response.text:
                    return None
                else:
                    logger.error("Situação inesperada na execução")

        return processo_codigo

    async def _consultar_processo(self, processo_codigo):
        """
        Consulta os detalhes de um processo usando o código do processo.

        :param processo_codigo: Código do processo judicial a ser consultado.
        :return: Conteúdo HTML do processo.
        """
        # Realiza uma solicitação HTTP para obter os detalhes do processo.
        async with ClientSession() as client:
            response = await client.get(
                url=f"{self.url_base}/cposg5/show.do",
                params={
                    "processo.codigo": processo_codigo,
                }
            )
            return await response.text()

    @staticmethod
    def _extrair_dados(html):
        """
        Extrai os dados de interesse do HTML do processo judicial.

        :param html: Conteúdo HTML do processo.
        :return: Dicionário contendo os dados extraídos.
        """
        # Definição dos campos a serem extraídos.
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

        # Inicialização do extrator de dados.
        extractor = DataExtractor(html)

        # Extração dos dados e retorno.
        dados_extraidos = extractor.extract(fields_to_extract)
        return dados_extraidos
