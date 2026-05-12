from langchain_core.tools import tool
from database.connection import get_schema_details, check_with_explain, is_valid_sql

from graph import QueryAgentState


def get_db_schema_node(state: QueryAgentState) -> str:
    schema = get_schema_details()
    state["db_schema"] = schema
    return schema

def validate_sql_node(state: QueryAgentState) -> str:
    #Validates a SQL query using syntax checks and EXPLAIN.

    if not is_valid_sql(sql_query):
        return "Error: Generated SQL is invalid or incomplete (syntax error)."
    
    explain_error = check_with_explain(sql_query)
    if explain_error:
        return f"Error: SQL failed EXPLAIN check: {explain_error}"
    
    sql_query = state["sql_query"]
    state["is_query_valid"] = True
    return 1
