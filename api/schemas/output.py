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


class StatusSolicitacaoOutput(BaseModel):
    classe: str
    area: str
    assunto: str
    data_distribuicao: str
    juiz: str
    valor_acao: str
    partes_processo: list[str]
    lista_movimentacoes: list[dict]
