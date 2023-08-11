from unittest.mock import patch, Mock

from pytest import raises
from redis.exceptions import ConnectionError
from database.service import RedisConnection


def test_check_redis_client_connection_error():
    """Teste se a exceção ConnectionError é levantada quando há um erro ao se conectar."""
    connection = RedisConnection()

    with patch("database.service.StrictRedis.from_url", side_effect=ConnectionError("Redis offline")):
        with raises(ConnectionError):
            connection.check_redis_client()


def test_check_redis_client_successful_connection():
    """Teste se a conexão é estabelecida com sucesso."""
    connection = RedisConnection()
    mock_redis = Mock()

    with patch("database.service.StrictRedis.from_url", return_value=mock_redis):
        connection.check_redis_client()
        assert connection.redis_client == mock_redis


def test_get_data():
    """Teste a obtenção de dados do Redis."""
    connection = RedisConnection()
    mock_redis = Mock()
    mock_redis.get.return_value = "test_value"

    with patch("database.service.StrictRedis.from_url", return_value=mock_redis):
        result = connection.get_data("test_key")
        mock_redis.get.assert_called_with("test_key")
        assert result == "test_value"


def test_set_data():
    """Teste a definição de dados no Redis."""
    connection = RedisConnection()
    mock_redis = Mock()

    with patch("database.service.StrictRedis.from_url", return_value=mock_redis):
        connection.set_data("test_key", "test_value")
        mock_redis.set.assert_called_with("test_key", "test_value")
