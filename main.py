from logging import basicConfig, getLogger, DEBUG
from json import dumps, loads
from uuid import uuid4
import asyncio

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, JSONResponse

from api.exceptions import InvalidParameterError
from api.schemas.input import ConsultaProcessoInput, StatusSolicitacaoInput
from api.schemas.output import StatusSolicitacaoOutput, ConsultaProcessoOutput, ConsultaProcessoResponses, \
    StatusSolicitacaoResponses
from api.services.process_handler import process_request
from database.service import startup, shutdown, set_data, get_data

# Configurando o log
basicConfig(filename='app.txt',
            level=DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)

app = FastAPI(
    title="JusBrasil",
    description="API desenvolvida como desafio técnico para o JusBrasil.",
    version="1.0.0",
    redoc_url=None
)

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)


# Redirecionar a página inicial para /docs
@app.get("/", include_in_schema=False)
def read_root():
    logger.info("Raiz acessada")
    return RedirectResponse(url="/docs")


@app.exception_handler(InvalidParameterError)
def handle_invalid_parameter_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": str(exc)},
    )


@app.post("/consulta-processo", response_model=ConsultaProcessoOutput, responses=ConsultaProcessoResponses.responses())
async def consulta_processo(payload: ConsultaProcessoInput = Depends()):
    # Criar um número de solicitação
    solicitacao_id = str(uuid4())

    # Armazene os detalhes da consulta no Redis
    logger.info("Solicitação recebida, dados salvos no banco")
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


@app.get("/status-solicitacao/{numero_solicitacao}",
         response_model=StatusSolicitacaoOutput,
         responses=StatusSolicitacaoResponses.responses())
async def status_solicitacao(payload: StatusSolicitacaoInput = Depends()):
    dados_solicitacao = await get_data(payload.numero_solicitacao)

    # Verificar se o número da solicitação existe
    if dados_solicitacao is None:
        logger.info(f"Solicitação {payload.numero_solicitacao} não encontrada")
        return JSONResponse({"error": "Solicitação não encontrada"}, status_code=404)

    response = loads(dados_solicitacao)

    return JSONResponse(
        content=StatusSolicitacaoOutput.model_validate(response).model_dump(exclude_none=True),
        status_code=200
    )
