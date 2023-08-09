from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator, ValidationError


class ConsultaProcessoOutput(BaseModel):
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


class ExtractDataOutput(BaseModel):
    classe: str
    area: str
    assunto: str
    data_distribuicao: str
    juiz: Optional[str] = None
    valor_acao: Optional[str] = None
    partes_processo: list[dict]
    lista_movimentacoes: list[dict]


class ExtractDataSecondInstanceOutput(ExtractDataOutput):
    data_distribuicao: Optional[str] = None
    juiz: Optional[str] = None


class StatusSolicitacaoOutput(BaseModel):
    # cenário enquanto ainda está sendo processado
    numero_processo: Optional[str] = None
    sigla_tribunal: Optional[str] = None
    status: Optional[str] = None

    # cenário após processar os dados
    first_instance: Optional[ExtractDataOutput] = None
    second_instance: Optional[ExtractDataSecondInstanceOutput] = None
