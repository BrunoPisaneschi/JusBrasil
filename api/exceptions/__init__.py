class InvalidParameterError(Exception):
    def __init__(self, message="Parâmetro inválido"):
        self.message = message
        super().__init__(self.message)
