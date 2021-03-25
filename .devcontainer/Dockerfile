FROM python:3.6-slim as build

RUN apt update && apt install -y git

RUN adduser --disabled-password --gecos '' vscode

USER vscode

ENV PATH="~/.local/bin:$PATH"