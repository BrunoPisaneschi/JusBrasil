*** Settings ***
Library     Collections
Library     RequestsLibrary

*** Variables ***
${BASE_URL}             http://localhost:8000
${NUMERO_PROCESSO}      0710802-55.2018.8.02.0001
${SIGLA_TRIBUNAL}       TJAL

*** Test Cases ***
Consultar Processo E Verificar Status Da Solicitacao
    [Tags]    consulta
    Create Session    alias=Session    url=${BASE_URL}
    Consultar Processo    ${NUMERO_PROCESSO}    ${SIGLA_TRIBUNAL}
    Verificar Status Da Solicitacao    ${NUMERO_SOLICITACAO}

*** Keywords ***
Consultar Processo
    [Arguments]    ${numero_processo}    ${sigla_tribunal}
    ${payload}=    Create Dictionary    numero_processo=${numero_processo}    sigla_tribunal=${sigla_tribunal}
    ${response}=    POST On Session    Session    /consulta-processo    json=${payload}
    ${json_response}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${response.status_code}    200
    Set Global Variable    ${NUMERO_SOLICITACAO}    ${json_response}[numero_solicitacao]

Verificar Status Da Solicitacao
    [Arguments]    ${numero_solicitacao}
    ${max_attempts}=    Set Variable    5
    FOR    ${index}    IN RANGE    ${max_attempts}
        ${response}=    GET On Session    Session    /status-solicitacao/${numero_solicitacao}
        Should Be Equal As Strings  ${response.status_code}    200
        ${json_response}=   Set Variable    ${response.json()}
        Log     ${json_response}
        ${key_exists}=  Run Keyword And Return Status    Dictionary Should Contain Key    ${json_response}    first_instance
        Exit For Loop If    ${key_exists}
        Sleep   5s    # espera 5 segundos antes da próxima tentativa
    END
