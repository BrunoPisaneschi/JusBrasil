from time import sleep
from invoke import task


@task
def wait_for_docker(c):
    """
    Aguarda até que os containers Docker estejam prontos.
    Tenta verificar o status dos containers até 10 vezes, esperando 5 segundos entre cada tentativa.
    Se o status "Up" não for encontrado, o programa terminará com um erro.
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
    """
    print("Iniciando Docker...")
    c.run("docker-compose up -d")
    wait_for_docker(c)
    print("Docker iniciado.")


@task
def stop_docker(c):
    """
    Para os containers Docker usando o comando 'docker-compose down'.
    """
    print("Parando Docker...")
    c.run("docker-compose down")
    print("Docker parado.")


@task
def unit_tests(c):
    """
    Executa testes unitários usando pytest para testes assíncronos.
    """
    print("Rodando testes unitários com pytest-asyncio...")
    c.run("pytest --verbose -m asyncio")
    print("Testes unitários completados.")


@task
def integration_tests(c):
    """
    Inicia o Docker, aguarda até que esteja pronto e executa testes de integração com o Robot Framework.
    """
    start_docker(c)
    wait_for_docker(c)
    print("Rodando testes de integração com Robot Framework...")
    c.run("robot -d results tests/integration")
    print("Testes de integração completados.")


@task
def all_tests(c):
    """
    Executa todos os testes, incluindo testes unitários e de integração, garantindo que os containers Docker estejam ativos.
    """
    unit_tests(c)
    integration_tests(c)
    stop_docker(c)
