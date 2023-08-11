from socket import gaierror
from decouple import config
from redis import StrictRedis
from redis.exceptions import ConnectionError


class RedisConnection:
    """
    Classe para gerenciar a conexão com um servidor Redis.

    Inicializa a URL do Redis a partir das configurações e fornece métodos para manipular dados no Redis.

    :ivar redis_url: URL para a conexão com o servidor Redis.
    :ivar redis_client: Cliente para a conexão com o servidor Redis.
    """

    def __init__(self):
        """Inicializa a URL do Redis e o cliente como None."""
        self.redis_url = config("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None

    def check_redis_client(self):
        """
        Obtém o cliente Redis, criando uma nova conexão se ainda não tiver sido estabelecida.

        :raises ConnectionError: Se houver um erro de conexão com o Redis.
        :return: Cliente Redis.
        """
        if self.redis_client is None:
            try:
                self.redis_client = StrictRedis.from_url(self.redis_url)
            except (OSError, gaierror):
                raise ConnectionError("Redis offline")

    def get_data(self, key):
        """
        Obtém dados associados a uma chave no Redis.

        :param key: Chave para buscar no Redis.
        :return: Dados associados à chave, ou None se a chave não existir.
        """

        self.check_redis_client()
        return self.redis_client.get(key)

    def set_data(self, key, value):
        """
        Define um valor para uma chave no Redis.

        :param key: Chave para definir no Redis.
        :param value: Valor para definir para a chave.
        """
        self.check_redis_client()
        self.redis_client.set(key, value)

