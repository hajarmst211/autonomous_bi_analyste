# sql_generator.py

import os
from dotenv import load_dotenv
import sys
import re
from google import genai
from database.connection import get_schema_details, execute_query, check_with_explain
from google.genai import types
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

current_dir = os.path.dirname(__file__)
prompt_path = os.path.abspath(os.path.join(current_dir, "..", "prompts", "system_content.md"))


def get_system_instructions():
    schema_details = get_schema_details()
    prompt = open(prompt_path, 'r').read()
    prompt = prompt.format(schema = schema_details)
    return prompt


def strip_sql(raw: str) -> str:
    match = re.search(r"```(?:sql)?\n?(.*?)```", raw, re.DOTALL)
    raw = match.group(1) if match else raw
    raw = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", raw)
    
    return raw.strip()


def generate_sql(client_question: str, error_history: list):
    question_number = 0
    if error_history:
            client_question += "You have made these mistakes priviously"
            for attempt_question, err in error_history:
                client_question =+ f"Attempt: {attempt_question}, Error: {err}. "
                
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        config=types.GenerateContentConfig(
                system_instruction=get_system_instructions(),
                temperature=0,
                top_p=0.95,
                top_k=20,
                ),
        contents=client_question
        )

    question_number += 1
    return strip_sql(response.text.strip())


def get_answer_from_ai(user_question:str, max_retries = 4):
    error_history = []
    attempts = 0

    while attempts < max_retries:
        sql_query = generate_sql(user_question)
        explain_result = check_with_explain(sql_query)

        if explain_result != None:
            error_history[user_question] = explain_result
            attempts += 1
            continue

        execution_result = execute_query(sql_query)
        if execution_result["error"] != None:
            error_history[user_question] = execution_result
            attempts =+ 1
        
        else:
            return execution_result["data"]
    
        return {"error": "Max retries reached. Could not generate a valid query.", "history": error_history}



if __name__ == "__main__":
    question = "Who are the top 5 customers by total spend?"
    sql = generate_sql(question)
    print(f"Generated SQL:\n{sql}")
    

