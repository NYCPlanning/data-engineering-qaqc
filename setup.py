from setuptools import setup

setup(
    name="src",
    version="0.1",
    packages=["src"],
    install_requires=[
        "sqlalchemy",
        "psycopg2-binary",
        "pandas<1.1",
        "numpy",
        "streamlit",
        "plotly",
    ],
    zip_safe=False,
)
