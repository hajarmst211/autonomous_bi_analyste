import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
prompt_path = os.path.abspath(os.path.join(current_dir, "..", "prompts", "sql_generation_prompt.md"))
db_file_path = os.path.join(project_root, "ecommerce.db")

db_path = f"sqlite:///{db_file_path}"