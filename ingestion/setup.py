from setuptools import setup, find_packages

setup(
    name="data-pipeline-ingestion",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "boto3>=1.26.0",
        "kafka-python>=2.0.2",
        "pyarrow>=12.0.0",
        "pandas>=2.0.0",
        "jsonschema>=4.17.0",
        "python-json-logger>=2.0.0",
    ],
    python_requires=">=3.10",
)