import json
from langchain_core.messages import AIMessage, SystemMessage
from tools import extract_requirements, rag_search, compare_candidates, get_llm
from state import AgentState

def input_receiver_node(state: AgentState):
    """
    Captures user input and updates the raw JD if the input looks like a full job description.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}
    
    latest_msg = messages[-1].content
    
    # If it's a long message and no JD exists, treat it as the initial JD
    # We don't overwrite jd_raw blindly so we don't lose the original context
    if len(latest_msg) > 100 and not state.get("jd_raw"):
        return {"jd_raw": latest_msg}
    
    return {}

def parse_requirements_node(state: AgentState):
    """
    Calls the extraction tool on the raw JD and updates the state.
    """
    jd_raw = state.get("jd_raw", "")
    # Use the tool from Phase 2
    reqs = extract_requirements(jd_raw)
    return {"extracted_requirements": reqs}

def update_requirements_node(state: AgentState):
    """
    Refines existing requirements based on user feedback (e.g., "add 5 years React").
    """
    messages = state.get("messages", [])
    latest_msg = messages[-1].content
    current_reqs = state.get("extracted_requirements", {})
    
    prompt = (
        f"Update the following job requirements based on the user's latest instruction. "
        f"If the user asks for a specific number of candidates, include a 'num_candidates' integer key. "
        f"Output ONLY a valid JSON object with 'must_haves', 'nice_to_haves' lists, and optionally 'num_candidates'.\n\n"
        f"Current Requirements: {json.dumps(current_reqs)}\n"
        f"User Instruction: {latest_msg}"
    )
    
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=prompt)])
    
    new_reqs = current_reqs
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        new_reqs = json.loads(content)
    except Exception as e:
        print(f"Failed to update requirements: {e}")
        
    return {"extracted_requirements": new_reqs}

def search_resumes_node(state: AgentState):
    """
    Calls the RAG search tool with the current requirements.
    """
    reqs = state.get("extracted_requirements", {})
    # Grab the requested number of candidates, default to 10
    k_val = reqs.get("num_candidates", 10)
    candidates = rag_search(reqs, k=k_val)
    return {"retrieved_candidates": candidates}

def multi_round_screening_node(state: AgentState):
    """
    Filters candidates, does deep analysis on the top tier, and generates Hire/No-Hire tags.
    """
    candidates = state.get("retrieved_candidates", [])
    reqs = state.get("extracted_requirements", {})
    
    if not candidates:
        return {"shortlist": [], "current_analysis": {"error": "No candidates found to screen."}}
    
    # 1. Evaluate all candidates retrieved from the vector database without arbitrary slicing limits
    top_candidates = candidates
    
    # 2. Deep analysis: Head-to-head comparison
    comparison_result = compare_candidates(top_candidates, reqs)
    
    # 3. Final round: Tag Hire/No-Hire based on the deep analysis
    llm = get_llm()
    prompt = (
        f"Based on the following comparative matrix, output a JSON object mapping each Candidate Name "
        f"to either 'Hire' or 'No-Hire'. "
        f"CRITICAL EVALUATION CRITERIA: "
        f"1. You MUST be extremely lenient. If a candidate has the requested 'Must-Haves' (like React and Python), you MUST mark them as 'Hire' even if their Years of Experience is slightly below the requirement (e.g. 2 years instead of 3). "
        f"2. You MUST evaluate candidates relatively. Mark at least the top 3 or 4 candidates as 'Hire', selecting those whose skills closest match the core Job Requirements. "
        f"3. Missing a nice-to-have should never result in a No-Hire. "
        f"Output ONLY valid JSON, no markdown.\n\n"
        f"Job Requirements: {json.dumps(reqs)}\n\n"
        f"Comparison: {comparison_result}"
    )
    response = llm.invoke([SystemMessage(content=prompt)])
    
    hire_tags = {}
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        hire_tags = json.loads(content)
    except Exception:
        pass
        
    # Append the status to the candidate dicts
    for c in top_candidates:
        c_name = c.get('source', '').replace('.txt', '').replace('.docx', '').replace('_', ' ')
        c["status"] = hire_tags.get(c_name, "No-Hire")

    return {
        "shortlist": top_candidates, 
        "current_analysis": {"comparison": comparison_result, "hire_tags": hire_tags}
    }

def generate_report_node(state: AgentState):
    """
    Compiles reasoning, strengths, and gaps into a formatted markdown report.
    """
    analysis = state.get("current_analysis", {})
    shortlist = state.get("shortlist", [])
    
    if "error" in analysis:
        report = f"**Screening Error:** {analysis['error']}"
    else:
        report = "### 📊 Candidate Match Report\n\n"
        report += "**Comparative Analysis:**\n"
        report += analysis.get("comparison", "No comparison available.") + "\n\n"
        
        # Sort shortlist so 'Hire' candidates appear at the top
        shortlist.sort(key=lambda x: 0 if x.get('status') == 'Hire' else 1)
        
        report += "### 🎯 Final Recommendations\n\n"
        report += "| Candidate Name | Candidate ID | Decision |\n"
        report += "| :--- | :---: | :---: |\n"
        for c in shortlist:
            status = c.get('status', 'No-Hire')
            name = c.get('source', c.get('id')).replace('.txt', '').replace('.docx', '').replace('_', ' ')
            c_id = c.get('id', 'Unknown')
            status_md = f"**{status}**" if status == "Hire" else status
            report += f"| {name} | `{c_id}` | {status_md} |\n"
            
        report += "\n*Would you like me to refine the search or generate interview questions for a specific candidate?*"
        
    analysis["final_report"] = report
    return {"current_analysis": analysis, "messages": [AIMessage(content=report)]}

def chat_response_node(state: AgentState):
    """
    Answers conversational queries ("Why did X fail?") using the current_analysis state.
    """
    messages = state.get("messages", [])
    analysis = state.get("current_analysis", {})
    latest_msg = messages[-1].content
    
    prompt = (
        f"You are a helpful hiring assistant. Answer the user's query based ONLY on the following "
        f"context from our recent candidate screening:\n\n{json.dumps(analysis)}\n\n"
        f"User Query: {latest_msg}"
    )
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=prompt)])
    
    return {"messages": [AIMessage(content=response.content)]}

# ==========================================
# Routing Logic (Conditional Edge Functions)
# ==========================================

def intent_router(state: AgentState) -> str:
    """
    Determines the path of the graph based on the user's natural language input.
    """
    messages = state.get("messages", [])
    if not messages:
        return "parse_requirements"
    
    latest_msg = messages[-1].content
    llm = get_llm()
    
    prompt = (
        f"Analyze the user's message and determine their intent. Options:\n"
        f"- 'new_jd' (user provided a brand new job description)\n"
        f"- 'refine_search' (user is tweaking requirements, e.g., 'add react', 'must have 5 years')\n"
        f"- 'general_query' (user is asking a question about a candidate, the reasoning, or interview prep)\n\n"
        f"Output ONLY the exact string of the option.\n\nMessage: {latest_msg}"
    )
    
    response = llm.invoke([SystemMessage(content=prompt)])
    intent = response.content.strip().lower()
    
    if "new_jd" in intent:
        return "parse_requirements"
    elif "refine_search" in intent:
        return "update_requirements"
    else:
        return "chat_response"
