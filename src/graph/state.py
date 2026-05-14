from typing import List, TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage

class QueryAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add] 

    user_question: str
    error_history: Annotated[list[tuple[str, str]], operator.add]
    attempts: int
    db_schema: str

    prompt: str
    sql_query: str
    execution_result: str
    is_query_valid: bool
    

