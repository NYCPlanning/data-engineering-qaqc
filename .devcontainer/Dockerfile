FROM python:3.9-slim as build

RUN apt update && apt install -y git

RUN pip install -U black
RUN pip install -U bandit

RUN adduser --disabled-password --gecos '' vscode

USER vscode

ENV PATH="~/.local/bin:$PATH"