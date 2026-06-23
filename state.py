from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Represents the state of our Agentic Resume Matcher workflow.
    """
    # Conversation history with the user (adding new messages to the sequence)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Original Job Description provided by the user
    jd_raw: str
    
    # Parsed requirements (Must-haves and Nice-to-haves)
    extracted_requirements: dict
    
    # Initial RAG search results (list of candidate dictionaries)
    retrieved_candidates: list[dict]
    
    # Filtered/Ranked candidates after multi-round screening
    shortlist: list[dict]
    
    # Reasoning, strengths, and gaps calculated during analysis
    current_analysis: dict
