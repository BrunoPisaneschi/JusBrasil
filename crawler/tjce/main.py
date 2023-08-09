from decouple import config

from crawler.default.instances.first_instance import FirstInstance
from crawler.default.instances.second_instance import SecondInstance
from crawler.default.main import DefaultTJ


class TJCE(DefaultTJ):
    def __init__(self):
        super().__init__()
        self.url_base = config("URL_BASE_TJCE")
        self.codigo_tj = "8.06"
        self.first_instance = FirstInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)
        self.second_instance = SecondInstance(codigo_tj=self.codigo_tj, url_base=self.url_base)
