FROM python:3.9-slim as build

WORKDIR /app

COPY . .

RUN dev/install_python_packages.sh


CMD [ "./entrypoint.sh" ]

EXPOSE 5000
