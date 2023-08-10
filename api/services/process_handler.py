from logging import basicConfig, getLogger, INFO
from importlib import import_module
from json import dumps, loads
from api.schemas.output import StatusSolicitacaoOutput
from database.service import RedisConnection

# Configurando o log
basicConfig(filename='app.txt',
            level=INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


async def process_request(solicitacao_id: str):
    """
    Função assíncrona responsável por processar uma solicitação de captura de dados de um processo jurídico.
    Captura os dados com base no ID de solicitação, atualiza o status da solicitação e importa o módulo de captura
    correspondente ao tribunal, finalizando com a atualização do banco de dados.

    :param solicitacao_id: ID da solicitação a ser processada.
    """

    # Obtendo dados da solicitação do banco de dados
    redis = RedisConnection()
    await redis.startup()
    dados_solicitacao = await redis.get_data(solicitacao_id)
    await redis.shutdown()
    dict_dados_solicitacao = loads(dados_solicitacao)

    numero_processo = dict_dados_solicitacao.get("numero_processo")
    sigla_tribunal = dict_dados_solicitacao.get("sigla_tribunal")

    logger.info("Dados capturados, iniciando processo de captura")

    # Atualizando o status da solicitação para "Em processamento"
    redis = RedisConnection()

    await redis.startup()
    await redis.set_data(key=solicitacao_id, value=dumps({
        "numero_processo": numero_processo,
        "sigla_tribunal": sigla_tribunal,
        "status": "Em processamento"
    }))
    await redis.shutdown()

    # Importando o módulo específico do tribunal
    module = import_module(f"crawler.{sigla_tribunal.lower()}.main")

    # Obtendo a classe correspondente ao tribunal
    tj = getattr(module, sigla_tribunal.upper())

    # Capturando os dados do processo
    dados_capturados = await tj().capturar_dados(numero_processo=dict_dados_solicitacao.get("numero_processo"))

    logger.info("Dados capturados, encerrando solicitação.")

    # Atualizando o banco de dados com os dados capturados
    redis = RedisConnection()

    await redis.startup()
    await redis.set_data(
        key=solicitacao_id,
        value=dumps(StatusSolicitacaoOutput.model_validate(dados_capturados).model_dump(exclude_none=True))
    )
    await redis.shutdown()
    logger.info(f"Dados atualizados no banco para a solicitação {solicitacao_id}")
