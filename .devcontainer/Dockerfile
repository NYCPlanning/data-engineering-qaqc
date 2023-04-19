FROM python:3.11-slim as build

RUN export DEBIAN_FRONTEND=noninteractive

# Run environment setup script
COPY bash/ /bash/
COPY requirements.txt /.
RUN bash/setup_env.sh

# Set environment variables from building environment
ARG SQL_ENGINE_EDM_DATA=edm_data_placeholder_engine
ENV SQL_ENGINE_EDM_DATA ${SQL_ENGINE_EDM_DATA}

# Run dev environment setups
RUN apt-get install -y git
RUN pip install -U black
RUN pip install -U bandit

RUN adduser --disabled-password --gecos '' vscode

USER vscode