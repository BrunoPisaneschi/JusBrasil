from socket import gaierror
from decouple import config
from aioredis import create_redis_pool
from aioredis.errors import ConnectionClosedError


class RedisConnection:
    """
    Classe para gerenciar a conexão com um servidor Redis.

    Inicializa a URL do Redis a partir das configurações e fornece métodos para manipular dados no Redis.

    :ivar redis_url: URL para a conexão com o servidor Redis.
    :ivar redis_pool: Pool de conexões para o servidor Redis.
    """

    def __init__(self):
        """Inicializa a URL do Redis e a pool de conexões como None."""
        self.redis_url = config("REDIS_URL", "redis://localhost:6379")
        self.redis_pool = None

    async def get_redis_pool(self):
        """
        Obtém o pool de conexões Redis, criando uma nova conexão se ainda não tiver sido estabelecida.

        :raises ConnectionClosedError: Se houver um erro de conexão com o Redis.
        :return: Pool de conexões Redis.
        """
        if self.redis_pool is None:
            try:
                self.redis_pool = await create_redis_pool(self.redis_url)
            except (OSError, gaierror):
                raise ConnectionClosedError("Redis offline")
        return self.redis_pool

    async def startup(self):
        """
        Método para ser executado no início da aplicação.
        Estabelece a conexão com o Redis.
        """
        await self.get_redis_pool()

    async def shutdown(self):
        """
        Método para ser executado no encerramento da aplicação.
        Fecha a conexão com o Redis.
        """
        self.redis_pool.close()
        await self.redis_pool.wait_closed()

    async def get_data(self, key):
        """
        Obtém dados associados a uma chave no Redis.

        :param key: Chave para buscar no Redis.
        :return: Dados associados à chave, ou None se a chave não existir.
        """
        _redis_pool = await self.get_redis_pool()
        return await _redis_pool.get(key)

    async def set_data(self, key, value):
        """
        Define um valor para uma chave no Redis.

        :param key: Chave para definir no Redis.
        :param value: Valor para definir para a chave.
        """
        _redis_pool = await self.get_redis_pool()
        await _redis_pool.set(key, value)
