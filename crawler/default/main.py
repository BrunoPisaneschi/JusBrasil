class DefaultTJ:
    """
    Classe DefaultTJ representa uma estrutura básica para um Tribunal de Justiça.
    Essa classe define a interface comum para as classes concretas de diferentes tribunais.

    :param first_instance: Objeto responsável por gerenciar a primeira instância do tribunal.
    :param second_instance: Objeto responsável por gerenciar a segunda instância do tribunal.
    """

    def __init__(self):
        """
        Inicializa a classe DefaultTJ com instâncias nulas para as primeiras e segundas instâncias do tribunal.
        Esses atributos devem ser definidos pelas classes derivadas que representam tribunais específicos.
        """
        self.first_instance = None
        self.second_instance = None

    async def capturar_dados(self, numero_processo):
        """
        Método assíncrono para capturar dados tanto da primeira quanto da segunda instância do tribunal,
        usando o número do processo fornecido.

        :param numero_processo: O número do processo para o qual os dados devem ser capturados.
        :return: Um dicionário contendo os dados capturados para as duas instâncias do tribunal.
                 Retorna None para uma instância se os dados não forem encontrados.
        """
        # Captura os dados da primeira instância usando o número do processo
        first_instance_data = await self.first_instance.capturar_dados(numero_processo=numero_processo)

        # Captura os dados da segunda instância usando o número do processo
        second_instance_data = await self.second_instance.capturar_dados(numero_processo=numero_processo)

        if not first_instance_data and not second_instance_data:
            return None

        # Compila os dados capturados em um dicionário e retorna
        return {
            "first_instance": first_instance_data if first_instance_data else None,
            "second_instance": second_instance_data if second_instance_data else None
        }
