# connection.py

import os
from sqlalchemy import create_engine, inspect, text

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ecommerce.db"))
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL)

def get_db_connection():
    return engine.connect()

def execute_query(query: str)-> dict:
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            if result.returns_rows:
                return {"data":[dict(row._mapping) for row in result], "error":None}
            else:
                connection.commit()
                return {"data":f"Success: {result.rowcount} rows affected", "error": None} 
            
    except Exception as err:
        return {"data":None, "error":str(err)}
    

def get_schema_details():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    schema_output = []

    for table in tables:
        columns = inspector.get_columns(table)
        col_desc = [f"{c['name']} ({c['type']})" for c in columns]
        schema_output.append(f"Table: {table}:Columns: {', '.join(col_desc)}")

    return schema_output


def check_with_explain(query: str)-> Exception:
    explain_query = f"EXPLAIN {query}"
    try:
        with engine.connect() as connection:
            connection.execute(text(explain_query))
            return None 
    except Exception as e:
        return e
    
    
def is_valid_sql(sql: str)_-> bool:
    return sql.strip().endswith(";") and "select" in sql.lower()