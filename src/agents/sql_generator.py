# sql_generator.py

import os
from dotenv import load_dotenv
import sys
import re
import time
from google import genai
from openai import OpenAI
from database.connection import get_schema_details, execute_query, check_with_explain, is_valid_sql
from google.genai import types, errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
#client = genai.Client(api_key=api_key)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

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


def call_with_retry(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            wait = 2 ** i
            print(f"Retry {i+1}, waiting {wait}s...")
            time.sleep(wait)
    raise Exception("Max retries reached")


def generate_sql(client_question: str, error_history: list):
    question_number = 0
    if error_history:
        client_question += " You previously made these mistakes:\n"
        for attempt, err in error_history:
            client_question += f"- SQL: {attempt}\n  Error: {err}\n"
                
    """response = client.models.generate_content(
        #model='gemini-2.0-flash',
        model='gemini-1.5-flash',
        config=types.GenerateContentConfig(
                system_instruction=get_system_instructions(),
                temperature=0,
                top_p=0.95,
                top_k=20,
                ),
        contents=client_question
        )
    """

    response = call_with_retry(
                lambda:client.chat.completions.create(
                model="llama3-70b-8192",
                messages=client_question,
                temperature=0
                ))
    question_number += 1
    return strip_sql(response.text.strip())


def get_answer_from_ai(user_question:str, max_retries = 4):
    error_history = []
    attempts = 0

    while attempts < max_retries:
        try:
            sql_query = generate_sql(user_question, error_history)

            if not is_valid_sql(sql_query):
                error_history.append((sql_query, "Incomplete SQL"))
                attempts += 1
                continue

            explain_result = check_with_explain(sql_query)
            if explain_result != None:
                error_history.append((user_question, explain_result))
                attempts += 1
                continue

            execution_result = execute_query(sql_query)
            if execution_result["error"] != None:
                error_history[user_question] = execution_result
                attempts += 1
            
            else:
                return execution_result["data"]
        

        except errors.ClientError as e:
            if "429" in str(e):
                print("Rate limit hit! Waiting 30 seconds...")
                time.sleep(30) 
            else:
                return {"error": f"AI API Error: {str(e)}"}
                
    return {"error": "Max retries reached."}


if __name__ == "__main__":
    question = "Show me the names of all products that cost more than 100 dollars"
    
    final_data = get_answer_from_ai(question)
    
    if isinstance(final_data, list):
        for row in final_data:
            print(row)
    else:
        print(final_data)
    

