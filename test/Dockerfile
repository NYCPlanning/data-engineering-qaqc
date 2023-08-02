FROM python:3.11-slim as build

ARG app_dir=test

# Run environment setup script
COPY test/bash/ bash/
COPY test/requirements.txt .
RUN bash/setup_env.sh

# Run deployed environment setups
WORKDIR /app

COPY test .

CMD [ "./entrypoint.sh" ]

EXPOSE 5000
