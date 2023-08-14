# JusBrasil
Desafio técnico proposto pela equipe do JusBrasil, que consiste em uma API capaz de receber números de processos dos TJs de AL e CE, capturar e retornar as informações disponíveis tanto em primeira instância, como segunda, sendo os dados:
- Classe 
- Area 
- Assunto 
- Data de distribuição 
- Juíz 
- Valor da ação 
- Partes do processo 
- Lista das movimentações (data e movimento)

## Execução
Crie uma virtual env ou instale diretamente no seu Python global a lib `invoke` com o comando abaixo.
```shell
pip install invoke==2.2.0
```

Essa lib esta dentro do requirements-dev, porém, apenas ela é necessaria fora do docker. 
Caso não queira, é possivel visualizar os comandos utilizados no arquivo `tasks.py` e reproduzí-los manualmente.

O projeto está configurado para ser executado no docker, então basta rodar o seguinte comando
```shell
inv start-docker
```
Assim que o projeto estiver rodando, acesse o [localhost](http://127.0.0.1:8000).

Para parar, execute:
```shell
inv stop-docker
```

## .ENV
Devido este ser um projeto de desafio técnico, foi incluído no repositório o arquivo `.env`.

## Testes
Foi implementado os testes unitários e testes de integração.
Abaixo, segue uma breve descrição da implementação e como executá-los, ao final da execução completa, irá desativar o docker.

Caso queira executar ambos de uma vez, execute este comando:
```shell
inv all-tests
```
### Testes unitários
Para realizar esses testes, foi utilizado a biblioteca `unit-tests`.

Com o comando abaixo, é possível executar todos os testes unitários, que estão salvos no diretório `tests\unit`
```shell
inv unit-tests
```
  
### Testes de integração
Para estes testes foi utilizado o framework chamado `robot-framework`.

Este framework irá realizar requisições a API e validar os resultados, para isso, **é necessário que a API esteja em execução**, caso contrário, será lançado um erro.

Mas fique tranquilo, pois com o comando abaixo, já está tudo feito para garantir que a API seja executada antes dos testes.
```shell
inv integration-tests
```
  
Para conferir o conteúdo dos testes de integração, ele está salvo no caminho `tests\integration`.
O arquivo `.robot` é o arquivo principal.
