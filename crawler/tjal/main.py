from decouple import config

from crawler.tjal.instances.first_instance import FirstInstance
from crawler.tjal.instances.second_instance import SecondInstance


class TJAL:
    def __init__(self):
        self.url_base = config("URL_BASE_TJAL")
        self.codigo_tj = "8.02"
        self.first_instance = FirstInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)
        self.second_instance = SecondInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)

    async def capturar_dados(self, numero_processo):
        first_instance_data = await self.first_instance.capturar_dados(numero_processo=numero_processo)
        second_instance_data = await self.second_instance.capturar_dados(numero_processo=numero_processo)
        return {
            "first_instance": first_instance_data if first_instance_data else None,
            "second_instance": second_instance_data if second_instance_data else None
        }
