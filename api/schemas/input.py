from typing import Literal
from uuid import UUID
from re import fullmatch

from pydantic import BaseModel, model_validator, Field

from api.exceptions import InvalidParameterError

# Definição de uma constante para as siglas dos tribunais disponíveis para consulta.
SIGLAS_TRIBUNAIS_DISPONIVEIS = Literal['TJAL', 'TJCE']


class ConsultaProcessoInput(BaseModel):
    """Modelo de entrada para consulta de um processo."""

    numero_processo: str = Field(max_length=25,
                                 min_length=25)  # Número do processo, com comprimento fixo de 25 caracteres.
    sigla_tribunal: SIGLAS_TRIBUNAIS_DISPONIVEIS  # Sigla do tribunal que pertence ao processo, deve estar na lista de siglas disponíveis.

    @model_validator(mode="before")
    def valida_numero_processo(self):
        """
        Valida o campo numero_processo, verificando se ele segue o padrão NNNNNNN-DD.AAAA.J.TR.OOOO.

        :raises InvalidParameterError: se numero_processo não for compatível com o padrão especificado.
        """
        numero_processo = self.get("numero_processo", '')
        pattern = r'\d{7}-\d{2}\.\d{4}\.8\.\d{2}\.\d{4}'
        result = fullmatch(pattern, numero_processo)
        if not result:
            raise InvalidParameterError(
                f"numero_processo '{numero_processo}' não é compatível com o padrão NNNNNNN-DD.AAAA.J.TR.OOOO"
            )
        return self


class StatusSolicitacaoInput(BaseModel):
    """Modelo de entrada para consulta do status de uma solicitação."""

    numero_solicitacao: str  # Número de solicitação no formato UUID.

    @model_validator(mode="before")
    def valida_numero_solicitacao(self):
        """
        Valida o campo numero_solicitacao, verificando se ele está no formato UUID.

        :raises InvalidParameterError: se numero_solicitacao não for compatível com o formato UUID.
        """
        try:
            UUID(self.get("numero_solicitacao"))
            return self
        except ValueError:
            raise InvalidParameterError(
                f"numero_solicitacao '{self.get('numero_solicitacao')}' não é compatível com o formato UUID"
            )
