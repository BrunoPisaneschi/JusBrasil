from asyncio import sleep
from json import dumps

from api.schemas.output import StatusSolicitacaoOutput
from database.service import get_redis_pool


async def process_request(solicitacao_id: str):
    redis_pool = await get_redis_pool()

    dados_solicitacao = await redis_pool.get(solicitacao_id)

    # Simulando o processamento da solicitação (por exemplo, buscar dados de um banco de dados externo)
    await sleep(5)

    dados_capturados = {
        "classe": "Civil",
        "area": "Cível",
        "assunto": "Contratos",
        "data_distribuicao": "2022-01-01",
        "juiz": "Dr. João Silva",
        "valor_acao": "R$ 10.000,00",
        "partes_processo": [
            "Parte A",
            "Parte B"
        ],
        "lista_movimentacoes": [
            {
                "data": "2022-01-02",
                "movimento": "Em análise"
            }
        ]
    }

    # Simular a resposta
    await redis_pool.set(
        solicitacao_id,
        dumps(StatusSolicitacaoOutput.model_validate(dados_capturados).model_dump())
    )
