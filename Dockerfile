FROM python:3.13-slim

RUN apt-get update && apt-get install
RUN pip install uv

ARG DIR_TESTS=/home/tests

RUN mkdir -p ${DIR_TESTS}

COPY scenarios ${DIR_TESTS}/scenarios
COPY templates ${DIR_TESTS}/templates
COPY pyproject.toml ${DIR_TESTS}/
COPY uv.lock ${DIR_TESTS}/
COPY ./*.py ${DIR_TESTS}

WORKDIR ${DIR_TESTS}

RUN uv sync

EXPOSE 8089 5557

CMD ["tail", "-f", "/dev/null"]
