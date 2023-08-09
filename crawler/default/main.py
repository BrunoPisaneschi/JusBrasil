class DefaultTJ:
    def __init__(self):
        self.first_instance = None
        self.second_instance = None

    async def capturar_dados(self, numero_processo):
        first_instance_data = await self.first_instance.capturar_dados(numero_processo=numero_processo)
        second_instance_data = await self.second_instance.capturar_dados(numero_processo=numero_processo)
        return {
            "first_instance": first_instance_data if first_instance_data else None,
            "second_instance": second_instance_data if second_instance_data else None
        }
