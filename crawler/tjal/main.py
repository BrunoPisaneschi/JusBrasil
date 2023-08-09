from decouple import config

from crawler.default.main import DefaultTJ
from crawler.default.instances.first_instance import FirstInstance
from crawler.default.instances.second_instance import SecondInstance


class TJAL(DefaultTJ):
    def __init__(self):
        super().__init__()
        self.url_base = config("URL_BASE_TJAL")
        self.codigo_tj = "8.02"
        self.first_instance = FirstInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)
        self.second_instance = SecondInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)
