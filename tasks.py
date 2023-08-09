from time import sleep

from invoke import task


@task
def wait_for_docker(c):
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
    print("Iniciando Docker...")
    c.run("docker-compose up -d")
    print("Docker iniciado.")


@task
def stop_docker(c):
    print("Parando Docker...")
    c.run("docker-compose down")
    print("Docker parado.")


@task
def unit_tests(c):
    print("Rodando testes unitários com pytest-asyncio...")
    c.run("pytest --verbose -m asyncio")
    print("Testes unitários completados.")


@task
def integration_tests(c):
    start_docker(c)
    wait_for_docker(c)
    print("Rodando testes de integração com Robot Framework...")
    c.run("robot -d results tests/integration")
    print("Testes de integração completados.")


@task
def all_tests(c):
    unit_tests(c)
    integration_tests(c)
    stop_docker(c)
