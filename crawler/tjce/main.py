from decouple import config
from crawler.default.instances.first_instance import FirstInstance
from crawler.default.instances.second_instance import SecondInstance
from crawler.default.main import DefaultTJ


class TJCE(DefaultTJ):
    """
    Classe TJCE herda de DefaultTJ e representa o Tribunal de Justiça do Ceará (TJCE).
    Essa classe é responsável por configurar e gerenciar as instâncias de rastreamento do TJCE.

    :param url_base: URL base para o TJCE, pode ser configurada através da variável de ambiente URL_BASE_TJCE.
    :param codigo_tj: Código associado ao TJCE.
    :param first_instance: Instância responsável por gerenciar a primeira instância do tribunal.
    :param second_instance: Instância responsável por gerenciar a segunda instância do tribunal.
    """

    def __init__(self):
        """
        Inicializa a classe TJCE com suas configurações e instâncias.
        """
        # Chamada ao construtor da classe pai
        super().__init__()

        # Configurando a URL base através de uma variável de ambiente
        self.url_base = config("URL_BASE_TJCE")

        # Código específico do TJCE
        self.codigo_tj = "8.06"

        # Cria a primeira instância com o código e a URL base
        self.first_instance = FirstInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)

        # Cria a segunda instância com o código e a URL base
        self.second_instance = SecondInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)
