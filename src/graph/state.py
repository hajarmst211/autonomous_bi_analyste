from typing import TypedDict, Annotated
import operator

class QueryAgentState(TypedDict):
    user_question: str
    error_history: Annotated[list[tuple[str, str]], operator.add]
    attempts: int
    db_schema: str

    prompt: str
    sql_query: str
    execution_result: str
    is_query_valid: bool
    

