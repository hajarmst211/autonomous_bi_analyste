#llm_config.py

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(
    openai_api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    timeout=60
)