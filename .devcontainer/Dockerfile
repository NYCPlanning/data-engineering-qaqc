FROM python:3.9-slim as build

RUN apt update && apt install -y git
RUN pip install -U black
RUN pip install -U bandit
RUN pip install -U poetry

RUN adduser --disabled-password --gecos '' vscode

USER vscode
ENV PATH="~/.poetry/bin:$PATH"
ENV PATH="~/.local/bin:$PATH"