# Demo Video Recording Script (5-6 Minutes)

This script provides a structured walkthrough for your final assignment demo video. It ensures you cover all the grading criteria outlined in `problemstatment.md`.

## 0:00 - 0:30: Introduction & Architecture
* **Visual:** Show the `agent_architecture.md` file (specifically the Mermaid state diagram).
* **Talking Points:**
  * Introduce the project: an AI-Powered Resume Matcher using LangGraph.
  * Briefly explain the graph structure: "The agent takes an input, uses an LLM to route intent, extracts requirements, searches the RAG vector store, performs deep screening, and has a human-in-the-loop breakpoint."

## 0:30 - 1:30: Flow 1 - Standard JD Parsing & Screening
* **Visual:** Open the Streamlit UI (`streamlit run app.py`).
* **Action:** Paste a sample Job Description into the chat.
* **Talking Points:**
  * Explain that the agent is currently hitting the `parse_requirements_node` to structure the data into must-haves and nice-to-haves.
  * Show the resulting report when it appears. Highlight the comparative matrix and the binary Hire/No-Hire recommendations.

## 1:30 - 3:00: Flow 2 - Explainability (The "Why?")
* **Visual:** Keep the Streamlit UI open on the generated report.
* **Action:** Type: *"Why did [Candidate ID] rank higher than [Other Candidate ID]?"* or *"Why is [Candidate ID] a No-Hire?"*
* **Talking Points:**
  * Emphasize that the agent is *not* running a new search.
  * Explain the `chat_response_node`: It accesses LangGraph's conversational memory (`AgentState['current_analysis']`) to pull the reasoning trace and explain its decision transparently to the recruiter.

## 3:00 - 4:30: Flow 3 - Iterative Refinement
* **Visual:** Streamlit UI.
* **Action:** Type: *"Actually, let's change the requirements. Make 5+ years of React a strict must-have."*
* **Talking Points:**
  * Explain the `intent_router` conditional edge. It detects that the user wants to tweak parameters, not start over.
  * It routes to `update_requirements_node`, modifies the state memory, and automatically triggers a re-ranking.
  * Show the new report and point out how the candidates shifted based on the new React requirement.

## 4:30 - 5:30: Code Walkthrough (Under the Hood)
* **Visual:** Open your IDE (VS Code/Cursor). Show `matching_agent.py` and `state.py`.
* **Talking Points:**
  * Show the `TypedDict` in `state.py` to prove how history, JDs, and shortlists are tracked.
  * Show `matching_agent.py` to highlight the `MemorySaver` checkpointer and the explicit graph edges.
  * Mention the LLM used (Groq) for fast inference.

## 5:30 - 6:00: Conclusion
* **Talking Points:**
  * Summarize the value: It automates manual screening, provides transparent reasoning to remove bias, and allows recruiters to dynamically converse with their data.
  * End the video.
