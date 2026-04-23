# connection.py

import os
from sqlalchemy import create_engine, inspect

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ecommerce.db"))
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL)

def get_db_connection():
    return engine.connect()

def run_query(query: str):

    with engine.connect() as connection:
        result = connection.execute(query)
        return [dict(row._mapping) for row in result]