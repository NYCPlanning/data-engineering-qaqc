FROM python:3.9-slim as build

WORKDIR /app

COPY . .

# RUN python3 -m venv venv

RUN pip3 install poetry
RUN poetry install


CMD [ "./entrypoint.sh" ]

EXPOSE 5000
