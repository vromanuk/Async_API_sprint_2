FROM python:3.9.6-buster

RUN useradd -ms /bin/bash tarantino
WORKDIR /app
# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY --chown=tarantino:tarantino ["./pyproject.toml", "./poetry.lock*", "/app/"]
EXPOSE 8000

RUN poetry install --no-root

COPY --chown=tarantino:tarantino ["./", "/app/src"]
USER tarantino

CMD uvicorn src.main:app --host 0.0.0.0 --port 8000
