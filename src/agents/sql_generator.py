# sql_generator.py

import os
from dotenv import load_dotenv
from database.connection import get_schema_details

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

def format_prompt(client_question: str):
    schema_details = get_schema_details()
    prompt = open('prompts/sql_generator.md', 'r').read()
    prompt = prompt.format(schema = schema_details, question = client_question)

    

