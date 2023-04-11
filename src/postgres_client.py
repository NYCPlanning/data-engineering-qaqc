import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from psycopg2.extensions import AsIs
import pandas as pd

load_dotenv()

BUILD_ENGINE = os.getenv("SQL_ENGINE_EDM_DATA", "")
SQL_FILE_DIRECTORY = ".data/sql"


def load_data_from_sql_dump(table_name: str) -> pd.DataFrame:
    print(f"Loading data into table {table_name} ...")
    file_name = f"{table_name}.sql"
    execute_sql_file_low_level(filename=file_name)
    table_names = execute_sql_select_query(
        """
        SELECT * FROM information_schema.tables;
        """
    )
    return table_names 


def create_sql_schema(schema_name: str) -> pd.DataFrame:
    placeholders = {"schema_name": AsIs(schema_name)}
    create_schema_query = """
        CREATE SCHEMA IF NOT EXISTS :schema_name
    """
    execute_sql_query(create_schema_query, placeholders)
    schema_names = execute_sql_select_query(
        """
        SELECT schema_name
        FROM :information_schema_name.schemata;
        """,
        {"information_schema_name": AsIs("information_schema")},
    )
    return schema_names


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
    os.system(f"postgres {BUILD_ENGINE} --set ON_ERROR_STOP=1 --file {filename}")