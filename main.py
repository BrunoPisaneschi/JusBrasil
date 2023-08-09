from json import dumps, loads
from uuid import uuid4
import asyncio

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, JSONResponse

from api.schemas.input import ConsultaProcessoInput, StatusSolicitacaoInput
from api.schemas.output import StatusSolicitacaoOutput, ConsultaProcessoOutput
from api.services.process_handler import process_request
from database.service import startup, shutdown, get_redis_pool

app = FastAPI()

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)


# Redirecionar a página inicial para /docs
@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.post("/consulta-processo", response_model=ConsultaProcessoOutput)
async def consulta_processo(payload: ConsultaProcessoInput = Depends()):
    redis_pool = await get_redis_pool()

    # Criar um número de solicitação
    solicitacao_id = str(uuid4())

    # Armazene os detalhes da consulta no Redis
    await redis_pool.set(solicitacao_id, dumps({
        "numero_processo": payload.numero_processo,
        "sigla_tribunal": payload.sigla_tribunal,
        "status": "Na Fila"
    }))

    response = {"numero_solicitacao": solicitacao_id}

    asyncio.create_task(process_request(solicitacao_id))

    return JSONResponse(
        content=ConsultaProcessoOutput.model_validate(response).model_dump(),
        status_code=200
    )


@app.get("/status-solicitacao/{numero_solicitacao}", response_model=StatusSolicitacaoOutput)
async def status_solicitacao(payload: StatusSolicitacaoInput = Depends()):
    redis_pool = await get_redis_pool()

    dados_solicitacao = await redis_pool.get(payload.numero_solicitacao.__str__())

    # Verificar se o número da solicitação existe
    if dados_solicitacao is None:
        return JSONResponse({"error": "Solicitação não encontrada."}, status_code=404)

    response = loads(dados_solicitacao.decode("utf-8"))

    return JSONResponse(
        content=StatusSolicitacaoOutput.model_validate(response).model_dump(),
        status_code=200
    )
