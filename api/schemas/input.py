from typing import Literal
from uuid import UUID
from re import fullmatch

from pydantic import BaseModel, model_validator, Field

from api.exceptions import InvalidParameterError

SIGLAS_TRIBUNAIS_DISPONIVEIS = Literal['TJAL', 'TJCE']


class ConsultaProcessoInput(BaseModel):
    numero_processo: str = Field(max_length=25, min_length=25)
    sigla_tribunal: SIGLAS_TRIBUNAIS_DISPONIVEIS

    @model_validator(mode="before")
    def valida_numero_processo(self):
        numero_processo = self.get("numero_processo", '')
        pattern = r'\d{7}-\d{2}\.\d{4}\.8\.\d{2}\.\d{4}'
        result = fullmatch(pattern, numero_processo)
        if not result:
            raise InvalidParameterError(
                f"numero_processo '{numero_processo}' não é compatível com o padrão NNNNNNN-DD.AAAA.J.TR.OOOO"
            )
        return self


class StatusSolicitacaoInput(BaseModel):
    numero_solicitacao: str

    @model_validator(mode="before")
    def valida_numero_solicitacao(self):
        try:
            UUID(self.get("numero_solicitacao"))
            return self
        except ValueError:
            raise InvalidParameterError(
                f"numero_solicitacao '{self.get('numero_solicitacao')}' não é compatível com o formato UUID"
            )
