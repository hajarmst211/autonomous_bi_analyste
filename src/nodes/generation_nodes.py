#prompt_nodes.py

from graph.state import QueryAgentState
from database.connection import get_schema_details, execute_query
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from database.connection import execute_query, check_with_explain, is_valid_sql
from config.paths import prompt_path, db_path
from config.llm_config import model
from agents.sql_generator import simple_generate_sql
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import ToolNode


db = SQLDatabase.from_uri(db_path)

toolkit = SQLDatabaseToolkit(db=db, llm=model)

tools = toolkit.get_tools()



def get_schema_node(state: QueryAgentState):
    
    db = SQLDatabase.from_uri(db_path)
    schema_info = db.get_table_info() 
    
    return {"db_schema": schema_info}



def get_instructions()-> str:
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
    return ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        ("human", "{question}")
    ])

def generate_query(state: QueryAgentState)-> str:
    question = state.get("user_question") or state["messages"][-1].content
    schema = state.get("db_schema", "No schema provided")
    prompt_template = get_instructions()
    chain = prompt_template | model
    
    response = chain.invoke({
        "question": question,
        "schema": schema
    })

    return {
        "sql_query": response.content,
        "messages": [response]
    }

#updates the state message (adds an error if the query is invalid or execution fails) and returns a boolean indicating if the query is valid and executed successfully
def validate_query(state: QueryAgentState) -> bool:
    sql_query = state.get("sql_query", "")
    if  not is_valid_sql(sql_query):
        return state["messages"].append(AIMessage(content="The generated SQL query is not valid. Please ensure it ends with a semicolon and contains a SELECT statement.")) or False
    
    check_error = check_with_explain(sql_query)
    if check_error is not None:
        return state["messages"].append(AIMessage(
                content="The generated SQL query failed the EXPLAIN check. Please revise your query.",
                additional_kwargs={"error_details": check_error}
                )) 

    execution_error = execute_query(sql_query).get("error")
    if  execution_error is not None:
        return state["messages"].append(AIMessage(
                content="The generated SQL query caused an execution error. Please review the error message and try again.",
                additional_kwargs={"error_details": execution_error}
                )) 
    
    return state["messages"].append(AIMessage(content="The generated SQL query is valid and executed successfully.")) 


def format_agent_output(messages: list):
    print("\n" + "="*50)
    print("                AGENT SESSION LOG")
    print("="*50)
    
    for i, msg in enumerate(messages):
        role = "USER" if isinstance(msg, HumanMessage) else "AGENT"
        
        # Color coding markers (optional)
        header = f"[{i+1}] {role}:"
        print(f"\n{header}")
        print("-" * len(header))
        
        # Format SQL if it looks like a query
        content = msg.content.strip()
        if "SELECT" in content.upper():
            print("SQL QUERY DETECTED:")
            print(f"  {content}")
        else:
            print(content)
            
        # Print Token Usage if it's an AI Message and has metadata
        if isinstance(msg, AIMessage) and msg.usage_metadata:
            tokens = msg.usage_metadata
            print(f"\n[Usage: Input {tokens.get('input_tokens')}, Output {tokens.get('output_tokens')}]")
            
    print("\n" + "="*50)

