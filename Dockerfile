# Utilize uma imagem oficial do Python
FROM python:3.11-slim-buster

# Defina uma variável de ambiente para garantir que a saída Python seja enviada diretamente para o terminal sem buffer
ENV PYTHONUNBUFFERED=1

# Crie e define o diretório de trabalho no contêiner
WORKDIR /app

# Instala as dependências necessárias
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta em que a aplicação irá rodar
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
