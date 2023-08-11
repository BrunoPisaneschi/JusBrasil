from time import sleep
from invoke import task


@task
def wait_for_docker(c):
    """
    Aguarda até que os containers Docker estejam prontos.
    Tenta verificar o status dos containers até 10 vezes, esperando 5 segundos entre cada tentativa.
    Se o status "Up" não for encontrado, o programa terminará com um erro.

    :param c: Uma instância de contexto fornecida pela biblioteca invoke.
    """
    print("Aguardando o Docker ficar pronto...")
    # Aguardar um tempo suficiente para os serviços estarem prontos
    for _ in range(10):
        result = c.run("docker-compose ps", hide=True)
        if "Up" in result.stdout:
            print("Docker está pronto.")
            sleep(2)
            return
        sleep(5)
    print("Tempo limite atingido. Docker pode não estar pronto.")
    exit(1)


@task
def start_docker(c):
    """
    Inicia os containers Docker usando o comando 'docker-compose up'.

    :param c: Uma instância de contexto fornecida pela biblioteca invoke.
    """
    print("Iniciando Docker...")
    c.run("docker-compose up -d")
    wait_for_docker(c)
    print("Docker iniciado.")


@task
def stop_docker(c):
    """
    Para os containers Docker usando o comando 'docker-compose down'.

    :param c: Uma instância de contexto fornecida pela biblioteca invoke.
    """
    print("Parando Docker...")
    c.run("docker-compose down")
    print("Docker parado.")


@task
def unit_tests(c):
    """
    Executa testes unitários usando pytest para testes assíncronos.

    :param c: Uma instância de contexto fornecida pela biblioteca invoke.
    """
    print("Rodando testes unitários com pytest-asyncio...")
    c.run("pytest --verbose")
    print("Testes unitários completados.")


@task
def integration_tests(c):
    """
    Inicia o Docker, aguarda até que esteja pronto e executa testes de integração com o Robot Framework.

    :param c: Uma instância de contexto fornecida pela biblioteca invoke.
    """
    start_docker(c)
    wait_for_docker(c)
    print("Rodando testes de integração com Robot Framework...")
    c.run("robot -d results tests/integration")
    print("Testes de integração completados.")


@task
def coverage(c):
    """
    Executa testes usando coverage e exibe um relatório de cobertura.

    Esta função executa o conjunto de testes com pytest sob a supervisão do coverage
    e, em seguida, produz um relatório de cobertura no terminal. Foi projetada
    para fornecer uma rápida visão geral de quais partes do código foram
    testadas e quais não foram.

    :param c: Uma instância de contexto fornecida pela biblioteca invoke.
    """
    c.run("coverage run --omit=./tests/* -m pytest && coverage report")


@task
def all_tests(c):
    """
    Executa todos os testes, incluindo testes unitários e de integração, garantindo que os containers Docker estejam ativos.

    :param c: Uma instância de contexto fornecida pela biblioteca invoke.
    """
    unit_tests(c)
    integration_tests(c)
    stop_docker(c)
