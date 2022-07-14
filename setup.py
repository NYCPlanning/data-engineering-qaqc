from setuptools import setup

setup(
    name="src",
    version="0.1",
    packages=["src"],
    install_requires=[
        "sqlalchemy",
        "psycopg2-binary",
        "pandas",
        "numpy",
        "streamlit",
        "plotly",
        "python-dotenv",
        "boto3",
    ],
    zip_safe=False,
)