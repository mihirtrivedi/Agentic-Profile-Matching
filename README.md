# AI Resume Matcher Pro

An advanced, agentic Retrieval-Augmented Generation (RAG) system built with **LangGraph** and **Streamlit**. This application evaluates candidate resumes against job descriptions through multi-round screening and provides a conversational interface for iterative refinement and explainability.

## 🚀 Features
- **Conversational Interface:** Submit raw job descriptions or ask questions in natural language.
- **Iterative Refinement:** Ask the agent to tweak requirements (e.g., "Make AWS a nice-to-have") and watch it re-rank candidates on the fly.
- **Holistic Screening Engine:** Evaluates candidates not just on a strict keyword checklist, but on overall JD alignment and experience depth.
- **Explainability:** Ask the agent *why* a candidate was hired or rejected, and it will explain its reasoning based on the generated comparative matrix.
- **Persistent Sessions:** Chat history is saved and restored automatically via URL parameters.

## 🧠 State Machine Architecture (LangGraph)

Below is the visual representation of our agent's decision-making flow:

```mermaid
graph TD;
    %% Nodes
    start((START))
    input_receiver[Input Receiver]
    router{Intent Router}
    
    parse_req[Parse Requirements]
    update_req[Update Requirements]
    search[Vector RAG Search]
    screen[Multi-Round Screening]
    report[Generate Report]
    chat[Chat Response & Explainability]
    
    end_node((END))

    %% Edges
    start --> input_receiver
    input_receiver --> router
    
    router -- "new_jd" --> parse_req
    router -- "refine_search" --> update_req
    router -- "general_query" --> chat
    
    parse_req --> search
    update_req --> search
    
    search --> screen
    screen --> report
    
    report --> end_node
    chat --> end_node
```

## 🛡️ Security Features
- **API Key Protection:** Uses `.dotenv` and a strict `.gitignore` to prevent secret leakage.
- **XSS Prevention:** All user inputs are strictly sanitized and HTML-escaped before rendering in the Streamlit UI.
- **State Isolation:** Each user/tab is assigned a unique UUID to prevent cross-session data contamination.

## ⚙️ Setup & Installation (For Reviewers/QA)
To run this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mihirtrivedi/Agentic-Profile-Matching.git
   cd Agentic-Profile-Matching
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
4. **Initialize the Vector Database:**
   Because the local `chroma_db` is safely ignored from version control, you must run the ingestion script first to populate the database with the sample resumes:
   ```bash
   python ingest_resumes.py
   ```
5. **Run the Streamlit App:**
   ```bash
   streamlit run app.py
   ```

## 🛠️ Tech Stack
- **UI:** Streamlit
- **Agent Framework:** LangChain & LangGraph
- **LLM:** Groq (llama-3.1-8b-instant)
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
- **Vector DB:** ChromaDB
