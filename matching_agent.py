from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import (
    parse_requirements_node,
    update_requirements_node,
    search_resumes_node,
    multi_round_screening_node,
    generate_report_node,
    chat_response_node,
    intent_router
)

def build_graph():
    """
    Constructs the LangGraph state machine for the AI Resume Matcher Agent.
    """
    # 1. Initialize the StateGraph using our AgentState schema
    workflow = StateGraph(AgentState)
    
    # 2. Add all isolated nodes from Phase 3
    workflow.add_node("parse_requirements", parse_requirements_node)
    workflow.add_node("update_requirements", update_requirements_node)
    workflow.add_node("search_resumes", search_resumes_node)
    workflow.add_node("multi_round_screening", multi_round_screening_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("chat_response", chat_response_node)
    
    # 3. Define the Conditional Routing Logic
    # After START, the intent_router decides where to go
    workflow.add_conditional_edges(
        START,
        intent_router,
        {
            "parse_requirements": "parse_requirements",
            "update_requirements": "update_requirements",
            "chat_response": "chat_response"
        }
    )
    
    # 5. Define explicit linear edges for the core execution pipelines
    # Both 'new jd' and 'update jd' funnel into the search logic
    workflow.add_edge("parse_requirements", "search_resumes")
    workflow.add_edge("update_requirements", "search_resumes")
    
    workflow.add_edge("search_resumes", "multi_round_screening")
    workflow.add_edge("multi_round_screening", "generate_report")
    
    # 6. Define END points
    workflow.add_edge("generate_report", END)
    workflow.add_edge("chat_response", END)
    
    # 7. Setup Checkpointing for Conversational Memory
    # This allows the graph to remember requirements and analysis across turns
    memory = MemorySaver()
    
    # 8. Compile the Graph
    app = workflow.compile(checkpointer=memory)
    
    return app

# Instantiate the compiled graph for external usage (e.g., in Streamlit app.py)
agent = build_graph()
