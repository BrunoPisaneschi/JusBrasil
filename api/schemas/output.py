from typing import Optional
from uuid import UUID
from pydantic import BaseModel, model_validator

from api.exceptions import InvalidParameterError


class ConsultaProcessoOutput(BaseModel):
    numero_solicitacao: str

    @model_validator(mode="before")
    def valida_numero_solicitacao(self):
        """
        Valida o campo numero_solicitacao, verificando se ele está no formato UUID.

        :raises ValidationError: se numero_solicitacao não for compatível com o formato UUID
        """
        try:
            UUID(self.get("numero_solicitacao"))
            return self
        except ValueError:
            raise InvalidParameterError(
                f"numero_solicitacao {self.get('numero_solicitacao')} não é compatível com o formato UUID"
            )


class ExtractDataOutput(BaseModel):
    """Modelo de saída para detalhes de um processo."""
    classe: str
    area: str
    assunto: str
    data_distribuicao: str
    juiz: Optional[str] = None
    valor_acao: Optional[str] = None
    partes_processo: list[dict]
    lista_movimentacoes: list[dict]


class ExtractDataSecondInstanceOutput(ExtractDataOutput):
    """Modelo de saída para detalhes de um processo em segunda instância. Deriva de ExtractDataOutput."""
    data_distribuicao: Optional[str] = None
    juiz: Optional[str] = None


class StatusSolicitacaoOutput(BaseModel):
    """Modelo de saída para status da solicitação de um processo."""

    # cenário enquanto ainda está sendo processado
    numero_processo: Optional[str] = None
    sigla_tribunal: Optional[str] = None
    status: Optional[str] = None

    # cenário após processar os dados
    first_instance: Optional[ExtractDataOutput] = None
    second_instance: Optional[ExtractDataSecondInstanceOutput] = None


class BaseError(BaseModel):
    """Modelo base para representar erros."""
    error: str


class DefaultResponses:
    """Classe base para respostas HTTP padrão."""

    @classmethod
    def _status_422(cls):
        """Resposta para o código de status 422 (Unprocessable Entity)."""
        return {
            422: {
                "model": BaseError,
                "description": "Parâmetro inválido",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Parâmetro inválido"
                        }
                    }
                },
            }
        }

    @classmethod
    def _status_500(cls):
        """Resposta para o código de status 500 (Internal Server Error)."""
        return {
            500: {
                "model": BaseError,
                "description": "Erro desconhecido no servidor, consulte os logs para maiores informações",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Erro desconhecido no servidor, consulte os logs para maiores informações"
                        }
                    }
                },
            }
        }

    @classmethod
    def responses(cls):
        """Método que agrega todas as respostas padrão."""
        return {k: v for method in dir(cls) if method.startswith("_status") for k, v in getattr(cls, method)().items()}


class ConsultaProcessoResponses(DefaultResponses):
    """Respostas para a consulta de processo."""

    @classmethod
    def _status_200(cls):
        """Resposta para o código de status 200 (OK) para a consulta de processo."""
        return {
            200: {
                "model": ConsultaProcessoOutput,
                "description": "Consulta enviada com sucesso para a fila",
                "content": {
                    "application/json": {
                        "example": {
                            "numero_solicitacao": "6fa125e6-e590-43c5-9de2-79d79695e24d"
                        }
                    }
                },
            }
        }

    @classmethod
    def _status_404(cls):
        """Resposta para o código de status 404 (Not Found) para a consulta de processo."""
        return {
            404: {
                "model": BaseError,
                "description": "Processo não encontrado",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Processo não encontrado"
                        }
                    }
                },
            }
        }


class StatusSolicitacaoResponses(DefaultResponses):
    """Respostas para a consulta de status de solicitação."""

    # Exemplo de processo para resposta
    processo_exemplo = {
        "first_instance": {
            "classe": "Penal",
            "area": "Criminal",
            "assunto": "Roubo",
            "data_distribuicao": "Sorteio",
            "juiz": "Dr. João Silva",
            "valor_acao": "5000,00",
            "partes_processo": [
                {
                    "Autor": "Mario Rossi",
                    "Defesa": {
                        "Advogado:": "Laura Bianchi"
                    }
                },
                {
                    "Autora": "Sara Moretti",
                    "Defesa": {
                        "Advogado:": "Fabio Verdi"
                    }
                },
                {
                    "Ré": "XYZ Construção Ltda.",
                    "Defesa": {
                        "Advogado:": "Roberto Alves",
                        "Advogada:": "Marta Ribeiro"
                    }
                },
                {
                    "Réu": "Banco Nacional",
                    "Defesa": {
                        "Advogado:": "Carlos Mendes"
                    }
                }
            ],
            "lista_movimentacoes": [
                {
                    "Data": "10/08/2023",
                    "Movimento": {
                        "titulo_movimentacao": "Ato Emitido",
                        "descricao_movimentacao": "Relação: 0123/2023\r\nData da Publicação: 12/08/2023\r\nNúmero do Diário: 7890"
                    }
                },
                {
                    "Data": "09/08/2023",
                    "Movimento": {
                        "titulo_movimentacao": "Inclusão no Diário da Justiça Eletrônico",
                        "descricao_movimentacao": "Relação: 0123/2023\r\nTeor do ato: Autos n°: 1234567-89.2023.9.10.0001 Ação: Procedimento Penal Réu: XYZ Construção Ltda. e outro ATO ORDINATÓRIO Prazo de 10 (dez) dias para recolhimento das custas processuais. São Paulo, 09 de agosto de 2023 Ana Maria Ferreira Analista\r\nAdvogados(s): Roberto Alves (OAB 12345/SP), Carlos Mendes (OAB 67890/SP), Fabio Verdi (OAB 11111/SP), Marta Ribeiro (OAB 22222/SP)"
                    }
                }
            ]
        },
        "second_instance": {
            "classe": "Recurso Penal",
            "area": "Criminal",
            "assunto": "Furto",
            "valor_acao": "2500,55",
            "partes_processo": [
                {
                    "Apelante:": "XYZ Construção Ltda.",
                    "Defesa": {
                        "Advogado:": "Roberto Alves",
                        "Advogada:": "Marta Ribeiro"
                    }
                },
                {
                    "Apelante:": "Banco Nacional",
                    "Defesa": {
                        "Advogado:": "Carlos Mendes"
                    }
                },
                {
                    "Apelado:": "Mario Rossi",
                    "Defesa": {
                        "Advogado:": "Laura Bianchi"
                    }
                },
                {
                    "Apelada:": "Sara Moretti",
                    "Defesa": {
                        "Advogado:": "Fabio Verdi"
                    }
                }
            ],
            "lista_movimentacoes": [
                {
                    "Data": "15/05/2023",
                    "Movimento": {
                        "titulo_movimentacao": "Certidão de Retorno ao 1º Grau",
                        "descricao_movimentacao": "Envio dos autos à instância de origem."
                    }
                },
                {
                    "Data": "16/05/2023",
                    "Movimento": {
                        "titulo_movimentacao": "Baixa Final",
                        "descricao_movimentacao": None
                    }
                }
            ]
        }
    }

    @classmethod
    def _status_200(cls):
        """Resposta para o código de status 200 (OK) para a consulta de status de solicitação."""
        return {
            200: {
                "model": StatusSolicitacaoOutput,
                "description": "Status solicitação/Solicitação concluída",
                "content": {
                    "application/json": {
                        "examples": {
                            "example1": {
                                "summary": "Status solicitação",
                                "value": {
                                    "numero_processo": "0113546-72.2018.8.02.0001",
                                    "sigla_tribunal": "TJAL",
                                    "status": "Na Fila"
                                }
                            },
                            "example2": {
                                "summary": "Dados capturados",
                                "value": cls.processo_exemplo
                            }
                        }
                    }
                }
            }
        }

    @classmethod
    def _status_404(cls):
        """Resposta para o código de status 404 (Not Found) para a consulta de status de solicitação."""
        return {
            404: {
                "model": BaseError,
                "description": "Solicitação não encontrada",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Solicitação não encontrada"
                        }
                    }
                },
            }
        }
