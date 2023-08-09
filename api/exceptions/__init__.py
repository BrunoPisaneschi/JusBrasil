class InvalidParameterError(Exception):
    """Exceção personalizada lançada quando um parâmetro inválido é encontrado.

    Essa exceção é útil para capturar erros específicos relacionados a parâmetros
    inválidos em diferentes partes do código, tornando o tratamento de erros mais claro.

    :param message: Mensagem de erro personalizada, padrão é "Parâmetro inválido".
    """

    def __init__(self, message="Parâmetro inválido"):
        # Inicializa a exceção com a mensagem fornecida ou uma mensagem padrão.
        self.message = message
        super().__init__(self.message)  # Chama o construtor da classe base com a mensagem.
