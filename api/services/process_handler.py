from importlib import import_module
from json import dumps, loads

from api.schemas.output import StatusSolicitacaoOutput
from database.service import get_data, set_data


async def process_request(solicitacao_id: str):
    dados_solicitacao = await get_data(solicitacao_id)
    dict_dados_solicitacao = loads(dados_solicitacao)

    numero_processo = dict_dados_solicitacao.get("numero_processo")
    sigla_tribunal = dict_dados_solicitacao.get("sigla_tribunal")

    await set_data(key=solicitacao_id, value=dumps({
        "numero_processo": numero_processo,
        "sigla_tribunal": sigla_tribunal,
        "status": "Em processamento"
    }))

    module = import_module(f"crawler.{sigla_tribunal.lower()}.main")

    tj = getattr(module, sigla_tribunal.upper())

    dados_capturados = await tj().capturar_dados(numero_processo=dict_dados_solicitacao.get("numero_processo"))

    await set_data(
        key=solicitacao_id,
        value=dumps(StatusSolicitacaoOutput.model_validate(dados_capturados).model_dump(exclude_none=True))
    )
