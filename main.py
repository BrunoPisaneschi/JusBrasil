from json import dumps, loads
from uuid import uuid4
import asyncio

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, JSONResponse

from api.exceptions import InvalidParameterError
from api.schemas.input import ConsultaProcessoInput, StatusSolicitacaoInput
from api.schemas.output import StatusSolicitacaoOutput, ConsultaProcessoOutput
from api.services.process_handler import process_request
from database.service import startup, shutdown, set_data, get_data

app = FastAPI()

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)


# Redirecionar a página inicial para /docs
@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.exception_handler(InvalidParameterError)
def handle_invalid_parameter_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": str(exc)},
    )


@app.post("/consulta-processo", response_model=ConsultaProcessoOutput)
async def consulta_processo(payload: ConsultaProcessoInput = Depends()):
    # Criar um número de solicitação
    solicitacao_id = str(uuid4())

    # Armazene os detalhes da consulta no Redis
    await set_data(key=solicitacao_id, value=dumps({
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
    dados_solicitacao = await get_data(payload.numero_solicitacao.__str__())

    # Verificar se o número da solicitação existe
    if dados_solicitacao is None:
        return JSONResponse({"error": "Solicitação não encontrada."}, status_code=404)

    response = loads(dados_solicitacao.decode("utf-8"))

    return JSONResponse(
        content=StatusSolicitacaoOutput.model_validate(response).model_dump(exclude_none=True),
        status_code=200
    )
