from typing import Literal
from uuid import UUID

from pydantic import BaseModel, model_validator, ValidationError

SIGLAS_TRIBUNAIS_DISPONIVEIS = Literal['TJAL', 'TJCE']


class ConsultaProcessoInput(BaseModel):
    numero_processo: str
    sigla_tribunal: SIGLAS_TRIBUNAIS_DISPONIVEIS


class StatusSolicitacaoInput(BaseModel):
    numero_solicitacao: str

    @model_validator(mode="before")
    def valida_numero_solicitacao(self):
        try:
            UUID(self.get("numero_solicitacao"))
            return self
        except ValueError:
            raise ValidationError(
                f"numero_solicitacao {self.get('numero_solicitacao')} não é compatível com o formato UUID"
            )
