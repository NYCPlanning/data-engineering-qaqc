FROM python:3.9-slim as build

WORKDIR /app

COPY . .

RUN pip3 install poetry
RUN poetry install


CMD [ "./entrypoint.sh" ]

EXPOSE 5000
