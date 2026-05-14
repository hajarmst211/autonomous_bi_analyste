# worklow.py

from state import QueryAgentState
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from langchain_core.messages import HumanMessage

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nodes.generation_nodes import get_schema_node, generate_query, format_agent_output, validate_query


workflow = StateGraph(QueryAgentState)

# Define the nodes
workflow.add_node("get_schema", get_schema_node)
workflow.add_node("generate_query", generate_query)
workflow.add_node("validate_query", validate_query)

# Build the edges
workflow.add_edge(START, "get_schema")
workflow.add_edge("get_schema", "generate_query")
workflow.add_edge("generate_query", "validate_query")
workflow.add_edge("validate_query", END)

app = workflow.compile()


inputs = {
    "user_question": "How many employees are in London?",
    "messages": [HumanMessage(content="How many employees are in London?")],
    "attempts": 0
}

result = app.invoke(inputs)
print(f"Generated SQL Query: {result['sql_query']}")
print(f"Execution Result: {format_agent_output(result['messages'])}")