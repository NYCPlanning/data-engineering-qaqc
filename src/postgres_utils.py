import os
import subprocess
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from psycopg2.extensions import AsIs
import pandas as pd

load_dotenv()

BUILD_ENGINE = os.getenv("SQL_ENGINE_EDM_DATA", "")
SQL_FILE_DIRECTORY = ".data/sql"
SOURCE_TABLE_NAME = lambda dataset, version: f"{dataset}_{version}"


def load_data_from_sql_dump(
    table_schema: str,
    dataset_by_version: str,
    dataset_name: str,
) -> list:
    print(f"Loading data into table {table_schema}.{dataset_name} ...")
    file_name = f"{dataset_by_version}.sql"
    # run sql dump file to create initial table
    execute_sql_file_low_level(filename=file_name)
    # copy inital data to a new table in the dataset-specific schema
    execute_sql_query(
        """
        CREATE TABLE :table_schema.:dataset_by_version AS TABLE :dataset_name
        """,
        {
            "table_schema": AsIs(table_schema),
            "dataset_by_version": AsIs(dataset_by_version),
            "dataset_name": AsIs(dataset_name),
        },
    )
    # copy inital data to a new table in the dataset-specific schema
    execute_sql_query(
        """
        DROP TABLE IF EXISTS :dataset_name CASCADE
        """,
        {
            "dataset_name": AsIs(dataset_name),
        },
    )
    table_names = get_schema_tables(table_schema=table_schema)
    return table_names


def get_schema_tables(table_schema: str) -> list:
    table_names = execute_sql_select_query(
        """
        SELECT table_name FROM information_schema.tables WHERE table_schema = :table_schema
        """,
        {"table_schema": table_schema},
    )

    return sorted(table_names["table_name"].to_list())


def get_table_columns(table_schema: str, table_name: str) -> list:
    columns = execute_sql_select_query(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = ':table_schema'
        AND table_name   = ':table_name';
        """,
        {"table_schema": AsIs(table_schema), "table_name": AsIs(table_name)},
    )
    return sorted(columns["column_name"])


def create_postigs_extension() -> None:
    query = "CREATE EXTENSION POSTIG"
    execute_sql_query(query)


def create_sql_schema(table_schema: str) -> pd.DataFrame:
    execute_sql_query(
        "DROP SCHEMA IF EXISTS :table_schema CASCADE",
        {"table_schema": AsIs(table_schema)},
    )
    execute_sql_query(
        "CREATE SCHEMA :table_schema", {"table_schema": AsIs(table_schema)}
    )
    table_schema_name = execute_sql_select_query(
        """
        SELECT schema_name
        FROM :table_schema.schemata;
        """,
        {"table_schema": AsIs("information_schema")},
    )
    return table_schema_name


def execute_sql_select_query(query: str, placeholders: dict = {}) -> pd.DataFrame:
    sql_engine = create_engine(BUILD_ENGINE)
    with sql_engine.begin() as sql_conn:
        select_records = pd.read_sql(sql=text(query), con=sql_conn, params=placeholders)

    return select_records


def execute_sql_query(query: str, placeholders: dict = {}) -> None:
    sql_engine = create_engine(BUILD_ENGINE)
    with Session(sql_engine) as session:
        session.execute(statement=text(query), params=placeholders)
        session.commit()


def execute_sql_file(filename: str) -> None:
    print(f"Executing {SQL_FILE_DIRECTORY}/{filename} ...")
    sql_file = open(f"{SQL_FILE_DIRECTORY}/{filename}", "r")
    sql_query = ""
    for line in sql_file:
        # ignore comment lines
        if line.strip("\n") and not line.startswith("--"):
            # append line to the query string
            sql_query += line.strip("\n")
            # if the query string ends with ';', it is a full statement
            if sql_query.endswith(";"):
                execute_sql_query(query=sql_query)
                sql_query = ""
            else:
                # continue parsing multi-line statement
                sql_query += " "
        else:
            continue


def execute_sql_file_low_level(filename: str) -> None:
    print()
    # TODO see if this can have a timeout
    subprocess.run(
        [
            f"psql {BUILD_ENGINE} --set ON_ERROR_STOP=1 --file {SQL_FILE_DIRECTORY}/{filename}"
        ],
        shell=True,
        check=True,
    )
