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
<<<<<<< HEAD
        "json"
=======
        "boto3",
>>>>>>> dev
    ],
    zip_safe=False,
)