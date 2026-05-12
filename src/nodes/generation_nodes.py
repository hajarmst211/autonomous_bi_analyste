#prompt_nodes.py

from graph import QueryAgentState, state
from database.connection import get_schema_details, execute_query

from database.connection import execute_query
from config import prompt_path
from agents.sql_generator import simple_generate_sql


def get_system_instructions_node(state: QueryAgentState) -> str:
    schema_details = get_schema_details()
    with open(prompt_path, 'r') as f:
        prompt_content = f.read()
    
    prompt = prompt_content.format(schema=schema_details)
    state["prompt"] = prompt
    return prompt
    

def generate_sql_node(state: QueryAgentState)-> dict:
    question = state["user_question"]
    history = state["error_history"]
    
    generated_sql = simple_generate_sql(question, history)

    state["sql_query"] = generated_sql
    return {
        "sql_query": generated_sql, 
        "attempts": state["attempts"] + 1
    }


def execute_query_node(state: QueryAgentState)-> dict:
    sql = state["sql_query"]
    
    result = execute_query(sql)
    
    if result.get("error"):
       
        return {"error_history": [(sql, result["error"])]}
    
    return {"final_result": result["data"]}