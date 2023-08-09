from socket import gaierror
from decouple import config
from aioredis import create_redis_pool
from aioredis.errors import ConnectionClosedError

# Configuração da URL do Redis, podendo ser definida através de variável de ambiente ou padrão
REDIS_URL = config("REDIS_URL", "redis://localhost:6379")

# Variável global para manter a referência para o pool de conexões Redis
redis_pool = None


async def get_redis_pool():
    """
    Obter o pool de conexões Redis.
    Cria uma nova conexão se ainda não tiver sido estabelecida.

    :raises ConnectionClosedError: Se houver um erro de conexão com o Redis.
    :return: Pool de conexões Redis.
    """
    global redis_pool
    if redis_pool is None:
        try:
            redis_pool = await create_redis_pool(REDIS_URL)
        except (OSError, gaierror):
            raise ConnectionClosedError("Redis offline")
    return redis_pool


async def startup():
    """
    Função para ser executada no início da aplicação.
    Estabelece a conexão com o Redis.
    """
    await get_redis_pool()


async def shutdown():
    """
    Função para ser executada no encerramento da aplicação.
    Fecha a conexão com o Redis.
    """
    redis_pool.close()
    await redis_pool.wait_closed()


async def get_data(key):
    """
    Obter dados associados a uma chave no Redis.

    :param key: Chave para buscar no Redis.
    :return: Dados associados à chave, ou None se a chave não existir.
    """
    _redis_pool = await get_redis_pool()
    return await _redis_pool.get(key)


async def set_data(key, value):
    """
    Definir um valor para uma chave no Redis.

    :param key: Chave para definir no Redis.
    :param value: Valor para definir para a chave.
    """
    _redis_pool = await get_redis_pool()
    await _redis_pool.set(key, value)
