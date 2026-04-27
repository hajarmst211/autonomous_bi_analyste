# sql_generator.py

import os
from dotenv import load_dotenv
import sys
from google import genai
from database.connection import get_schema_details
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

def generate_sql(client_question: str):


    response = client.models.generate_content(
    model='gemini-2.5-flash',\
    config=types.GenerateContentConfig(
        system_instruction=get_system_instructions(),
        temperature=0,
        top_p=0.95,
        top_k=20,
        ),
    contents=client_question
    )

    return response.text.strip()

if __name__ == "__main__":
    question = "Who are the top 5 customers by total spend?"
    sql = generate_sql(question)
    print(f"Generated SQL:\n{sql}")
    

