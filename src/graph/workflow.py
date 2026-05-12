# worklow.py

from state import QueryAgentState
from langgraph.graph import StateGraph, END
from langgraph.types import RetryPolicy

from nodes.db_nodes import get_db_schema_node, validate_sql_node

from nodes.generation_nodes import get_system_instructions_node, generate_sql_node, execute_query_node



workflow = StateGraph(QueryAgentState)


# Add Nodes
workflow.add_node("get_schema", get_db_schema_node)
workflow.add_node("format_system_instructions", get_system_instructions_node)
workflow.add_node("sql_generation",  generate_sql_node)
workflow.add_node("validation",validate_sql_node )
workflow.add_node("execute", execute_query_node)

# Entry Point
workflow.set_entry_point("get_schema")

# EDgesworkflow.add_edge("get_schema", "format_system_instructions")
workflow.add_edge("format_system_instructions", "sql_generation")
workflow.add_edge("sql_generation", "validation")

# Add Conditional Logic after Validation
workflow.add_conditional_edges(
    "validate",
    should_continue,
    {
        "retry": "generate",  
        "end": "execute"      
    }
)

workflow.add_conditional_edges(
    "execute",
    should_continue,
    {
        "retry": "generate",
        "end": END
    }
)

# Compile the Graph
app = workflow.compile()