# Implementation Plan: AI-Powered Resume Matcher Agent

This document breaks down the development of the LangGraph-based Resume Matcher into a phased implementation plan based on the problem statement and the defined agent architecture.

---

## Phase 1: Foundation & State Definition
**Goal:** Set up the basic infrastructure, dependencies, and define the core LangGraph state.

1. **Environment Setup:**
   - **LLM Engine:** The primary LLM used in this project is Groq (specifically `llama-3.1-8b-instant` via `langchain-groq`).
   - Initialize project and install dependencies (`langgraph`, `langchain-groq`, `streamlit` or `gradio`, etc.).
   - Configure Groq API keys and environment variables.
2. **State Definition (`state.py`):**
   - Create the `AgentState` class using `TypedDict`.
   - Define fields: `messages` (history), `jd_raw`, `extracted_requirements`, `retrieved_candidates`, `shortlist`, `current_analysis`, and `human_feedback`.
3. **Basic Interface Skeleton:**
   - Create the initial shell for the chat interface (e.g., a simple Streamlit chat UI or CLI loop) that will eventually pass messages to the graph.

---

## Phase 2: Tool Ecosystem Development
**Goal:** Build and integrate all the necessary tools the agent will use to perform its tasks.

1. **Integrate Legacy Tools:**
   - Wrap Milestone 1 file parsers (PDF, DOCX, TXT) into a callable `fs_tools` function.
   - Wrap Milestone 2 RAG system into a callable `rag_search` tool capable of taking parsed requirements and returning candidate profiles.
2. **Develop New Analysis Tools:**
   - `extract_requirements(jd: str)`: Create a prompt and tool to extract and structure 'must-haves' and 'nice-to-haves' from a raw JD.
   - `compare_candidates(candidate_ids: list)`: Build a prompt chain that takes two candidate profiles and generates a comparative matrix (strengths/weaknesses).
   - `generate_interview_questions(candidate_id: str)`: Build a tool that creates custom interview questions based on the candidate's specific gaps relative to the JD.

---

## Phase 3: LangGraph Node Implementation
**Goal:** Write the individual Python functions (nodes) that will make up the steps in the workflow.

1. **Routing & Parsing Nodes:**
   - `Input_Receiver`: Captures user input.
   - `Intent_Router`: Uses an LLM to decide if the user is giving a JD, adjusting criteria, or asking a question.
   - `Parse_Requirements`: Calls the `extract_requirements` tool and updates the state.
2. **Search & Screening Nodes:**
   - `Search_Resumes`: Calls the `rag_search` tool and populates `retrieved_candidates` in the state.
   - `Multi_Round_Screening`: 
     - Create logic for the initial fast-pass filter (Top 10).
     - Create logic for deep analysis on the Top 10 (calling `compare_candidates`).
     - Generate binary Hire/No-Hire tags.
3. **Reporting Node:**
   - `Generate_Report`: Compiles the reasoning, strengths, and gaps into a formatted markdown string stored in `current_analysis`.

---

## Phase 4: Graph Construction & Orchestration
**Goal:** Connect the nodes into a cohesive, cyclical state machine using LangGraph.

1. **Graph Assembly (`matching_agent.py`):**
   - Initialize the `StateGraph`.
   - Add all nodes created in Phase 3.
   - Define the explicit edges (e.g., `Parse_Requirements` $\rightarrow$ `Search_Resumes`).
2. **Conditional Logic:**
   - Implement the conditional edges from the `Intent_Router` to direct the flow dynamically based on the LLM's decision.
3. **Memory & Checkpointing:**
   - Integrate LangGraph's `MemorySaver` (or similar checkpointer) to maintain conversational context across multiple interactions, allowing the agent to "remember" previous filtering criteria.

---

## Phase 5: Interactive Features & Human-in-the-Loop
**Goal:** Enable iterative refinement and natural language queries about the agent's decisions.

1. **The Human Feedback Loop:**
   - Implement a breakpoint node (`Human_Feedback_Loop`) that interrupts the graph execution to return the report to the user and wait for feedback.
2. **Iterative Refinement Logic:**
   - Ensure the system can handle prompts like "Find candidates with React" followed by "Actually, make it 5 years experience" by updating the state and routing back to `Search_Resumes`.
3. **Explainability Queries:**
   - Implement the logic to handle questions like "Why did John rank higher than Jane?". The agent should pull from `current_analysis` in the state to formulate its conversational response without re-running the entire search.

---

## Phase 6: Testing, Refinement & Delivery
**Goal:** Polish the system and prepare for final submission.

1. **Scenario Testing:**
   - Create and test at least 5 distinct conversational flows (e.g., standard screening, changing requirements mid-stream, questioning the agent's logic).
2. **Prompt Tuning:**
   - Refine the Groq LLM prompts to ensure the reasoning trace is clear, objective, and accurate.
3. **Final Delivery Prep:**
   - Complete the codebase (`matching_agent.py` and interface).
   - Ensure the State Machine Diagram is accurate.
   - Record the 5-6 minute demo video showcasing the agent's reasoning and conversational capabilities.
