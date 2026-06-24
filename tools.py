import json
import re
from typing import List, Dict

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import streamlit as st

load_dotenv()



@st.cache_resource
def get_vector_store():
    """Initializes and returns the Chroma Vector Store using HuggingFace embeddings."""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    persist_directory = "./chroma_db"
    
    # We initialize the vector store. If db doesn't exist, it will be created.
    # In a real scenario, documents would be added here via Milestone 1 scripts.
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    return vectorstore

def rag_search(requirements: Dict, k: int = 10) -> List[Dict]:
    """
    Searches the vector database for candidates matching the requirements.
    (Wraps Milestone 2 functionality)
    """
    vectorstore = get_vector_store()
    
    # Construct a search query from must-haves and nice-to-haves, ensuring all items are cast to strings
    must_haves = ", ".join([str(item) for item in requirements.get("must_haves", [])])
    nice_to_haves = ", ".join([str(item) for item in requirements.get("nice_to_haves", [])])
    
    search_query = f"Must have skills: {must_haves}. Nice to have skills: {nice_to_haves}."
    
    # Perform similarity search
    # We catch exceptions in case the db is empty or uninitialized
    try:
        results = vectorstore.similarity_search_with_score(search_query, k=k)
        
        candidates = []
        for doc, score in results:
            candidates.append({
                "id": doc.metadata.get("candidate_id", "Unknown ID"),
                "source": doc.metadata.get("source", "Unknown Source"),
                "content": doc.page_content,
                "score": score
            })
        return candidates
    except Exception as e:
        print(f"RAG Search warning: {str(e)}")
        # Return mock data if db is empty for testing Phase 2 independently
        return [{"id": "mock_1", "content": "Mock resume with React and Python", "source": "mock_resume.pdf"}]

# ==========================================
# New Analysis Tools (Phase 2 core)
# ==========================================

def extract_json_block(text: str) -> str:
    """Extracts the outermost JSON block from LLM output, handling markdown and extra text."""
    # First, try to extract from a markdown code block
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        content = match.group(1)
    else:
        content = text
        
    # Then, isolate the JSON object by finding the first { and last }
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1 and end > start:
        return content[start:end+1]
    return content

def get_llm():
    """Returns the Groq LLM instance with a strict 1-retry limit to prevent hanging."""
    return ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_retries=1)

def extract_requirements(jd: str) -> Dict:
    """
    Parses a raw job description and extracts must-haves and nice-to-haves.
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert technical recruiter. Analyze the job description and extract the 'must_haves' and 'nice_to_haves'. "
                   "If the user specifies a number of candidates to return, include 'num_candidates' as an integer. "
                   "Output ONLY a valid JSON object with the keys 'must_haves', 'nice_to_haves', and optionally 'num_candidates'. "
                   "Do NOT wrap the response in markdown blocks. Do NOT include conversational text. Return ONLY the raw JSON dictionary."),
        ("human", "{jd}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"jd": jd})
    
    try:
        content = extract_json_block(response.content)
        requirements = json.loads(content)
        return requirements
    except Exception as e:
        print(f"Extraction failed: {e}")
        return {"must_haves": [], "nice_to_haves": []}

def compare_candidates(candidate_profiles: List[Dict], requirements: Dict) -> str:
    """
    Performs head-to-head comparison of candidates based on requirements.
    Expects a list of dictionaries containing candidate content.
    """
    if len(candidate_profiles) < 2:
        return "Not enough candidates to compare."
        
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert technical recruiter comparing candidate profiles against job requirements. "
                   "Your goal is to provide a highly objective, evidence-based comparative matrix formatted strictly as a Markdown Table. "
                   "The table must have the following columns: 'Candidate Name', 'Experience Match', 'Must-Haves Alignment', 'Nice-To-Haves Alignment', 'Missing Skills', and 'Overall JD Alignment'. "
                   "Do NOT include IDs in the table.\n"
                   "CRITICAL FORMATTING INSTRUCTIONS:\n"
                   "- Inside table cells, you MUST use `<br>` to force line breaks. Every single evaluated skill must be on a new line (e.g., `**[YES]** React <br> **[NO]** Python`).\n"
                   "Base your analysis STRICTLY on the provided text.\n\n"
                   "Job Requirements: {requirements}"),
        ("human", "Here are the candidate profiles:\n\n{profiles}")
    ])
    
    # Format profiles for the prompt
    formatted_profiles = ""
    for p in candidate_profiles:
        name = p.get('source', p.get('id')).replace('.txt', '').replace('.docx', '').replace('_', ' ')
        formatted_profiles += f"--- Candidate Name: {name} ---\n{p.get('content')}\n\n"
        
    chain = prompt | llm
    response = chain.invoke({
        "requirements": json.dumps(requirements),
        "profiles": formatted_profiles
    })
    
    return response.content


