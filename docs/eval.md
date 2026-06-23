# Phase-wise Evaluation Criteria

This document defines the evaluation criteria (Eval) for each phase of the Implementation Plan. These metrics will ensure that each component of the AI-Powered Resume Matcher functions correctly before moving to the next phase.

## Phase 1: Foundation & State Definition
**Goal:** Ensure the foundational architecture and state schemas are robust.
- [ ] **State Integrity:** The `AgentState` TypedDict compiles without errors and strictly enforces data types.
- [ ] **Environment Validation:** Groq API keys and LangGraph dependencies load successfully without runtime import errors.
- [ ] **Interface Stub:** The basic chat interface boots up and can accept a string input and return a mocked string output.

## Phase 2: Tool Ecosystem Development
**Goal:** Verify that all tools produce deterministic, highly accurate outputs.
- [ ] **`extract_requirements` Eval:** When given 3 different JDs, the tool correctly outputs a JSON object separating 'must-haves' and 'nice-to-haves' with 100% format adherence.
- [ ] **`rag_search` Eval:** Given a mock requirement, the tool successfully interfaces with the Milestone 2 vector store and returns a list of candidate dictionaries.
- [ ] **`compare_candidates` Eval:** The prompt chain consistently returns a comparative matrix outlining strengths and gaps without hallucinating skills not present in the input text.
- [ ] **`generate_interview_questions` Eval:** Questions generated are directly related to the "gaps" identified in the candidate's profile, not generic behavioral questions.

## Phase 3: LangGraph Node Implementation
**Goal:** Test the isolated logic of each node before graph assembly.
- [ ] **Node Mutability:** Each node function (e.g., `Parse_Requirements`, `Search_Resumes`) correctly takes an `AgentState`, performs its action, and returns a dictionary that appropriately updates the state without deleting historical data.
- [ ] **Screening Accuracy:** The `Multi_Round_Screening` node successfully takes a list of 10 candidates, applies the deep analysis prompt, and outputs a binary Hire/No-Hire tag for each.

## Phase 4: Graph Construction & Orchestration
**Goal:** Ensure the state machine routes intent correctly and maintains conversational memory.
- [ ] **Graph Compilation:** The `StateGraph` compiles into a `CompiledGraph` without edge routing errors.
- [ ] **Routing Accuracy (Intent Eval):** When tested with 10 distinct queries (e.g., "Here is a JD", "Compare them", "Why did he fail?"), the `Intent_Router` routes to the correct downstream node at least 90% of the time.
- [ ] **Memory Persistence:** The `MemorySaver` checkpointer successfully maintains the `extracted_requirements` across 3+ conversational turns.

## Phase 5: Interactive Features & Human-in-the-Loop
**Goal:** Validate the dynamic, interactive elements of the agent.
- [ ] **Breakpoint Triggering:** The graph consistently pauses execution at the `Human_Feedback_Loop` node and surfaces the current report to the frontend.
- [ ] **Iterative Re-ranking:** If the user inputs "Change the requirement from 3 years to 5 years", the graph successfully updates the state, loops back to the search/screening nodes, and produces a new, distinct shortlist.
- [ ] **Explainability:** When asked "Why did you rank X higher than Y?", the agent provides a response that directly references the data stored in `State['current_analysis']` without initiating a new RAG search.

## Phase 6: Testing, Refinement & Delivery
**Goal:** Final end-to-end validation for submission.
- [ ] **Flow Completion:** All 5 predefined test conversation flows can be executed from START to END without throwing an unhandled exception or entering an infinite loop.
- [ ] **UX Polish:** The CLI or Streamlit interface cleanly presents markdown tables, reasoning traces, and candidate data without breaking formatting.
- [ ] **Demo Readiness:** The system's response latency is acceptable for a 5-6 minute demo video (e.g., streaming responses or fast Groq inference times).
