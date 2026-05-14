import os
from dotenv import load_dotenv
import sys
import re
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.connection import get_schema_details, execute_query, check_with_explain, is_valid_sql

load_dotenv()

llm = ChatOpenAI(
    openai_api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    timeout=60
)

current_dir = os.path.dirname(__file__)
prompt_path = os.path.abspath(os.path.join(current_dir, "..", "prompts", "sql_generation_prompt.md"))

def get_system_instructions():
    schema_details = get_schema_details()
    with open(prompt_path, 'r') as f:
        prompt_content = f.read()
    return prompt_content.format(schema=schema_details)

def strip_sql(raw: str) -> str:
    match = re.search(r"```(?:sql)?\n?(.*?)```", raw, re.DOTALL)
    raw = match.group(1) if match else raw
    raw = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", raw)
    return raw.strip()


def simple_generate_sql(client_question: str):
    system_prompt = get_system_instructions()
    
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{question}")
    ])

    chain = prompt_template | llm | StrOutputParser()
    
    response = chain.invoke({"question": client_question})
    return strip_sql(response)


def generate_sql(client_question: str, error_history: list):
    system_prompt = get_system_instructions()
    
    if error_history:
        history_text = "\nPrevious failed attempts:\n"
        for attempt, err in error_history:
            history_text += f"- SQL: {attempt}\n  Error: {err}\n"
        client_question += history_text

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{question}")
    ])

    chain = prompt_template | llm | StrOutputParser()
    
    response = chain.invoke({"question": client_question})
    return strip_sql(response)

def get_answer_from_ai(user_question: str, max_retries=10):
    error_history = []
    attempts = 0

    while attempts < max_retries:
        try:
            print(f"Attempt {attempts + 1} to generate and execute SQL")
            sql_query = generate_sql(user_question, error_history)
            print(f"Generated SQL Query:\n{sql_query}\n")
            if not is_valid_sql(sql_query):
                print("Generated SQL is invalid or incomplete. Retrying...")
                error_history.append((sql_query, "Incomplete or invalid SQL syntax"))
                attempts += 1
                continue
            
            print(f"AI generated SQL. Now checking with EXPLAIN...")
            explain_result = check_with_explain(sql_query)
            if explain_result is not None:
                print("EXPLAIN check failed. SQL is not valid or may cause issues.")
                print(f"SQL failed EXPLAIN check: {explain_result}") 
                error_history.append((sql_query, explain_result))
                attempts += 1
                continue

            execution_result = execute_query(sql_query)
            if execution_result.get("error"):
                print("Checking the execution result for errors...")
                error_history.append((sql_query, execution_result["error"]))
                print("Execution error: ", execution_result["error"])
                attempts += 1
            else:
                print("SQL executed successfully!")
                return execution_result["data"]

        except Exception as e:
            if "429" in str(e):
                print("Rate limit hit! Waiting...")
                time.sleep(10)
                attempts += 1
            else:
                return {"error": f"AI Error: {str(e)}"}
                
    return {"error": "Max retries reached."}

if __name__ == "__main__":
    question = "Show me the names of all products"
    final_data = get_answer_from_ai(question)
    
    if isinstance(final_data, list):
        for row in final_data:
            print(row)
    else:
        print(final_data)