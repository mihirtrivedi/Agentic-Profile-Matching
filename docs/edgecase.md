# Edge Cases: AI-Powered Resume Matcher Agent

This document outlines potential edge cases and failure modes that need to be handled during the development of the LangGraph-based Resume Matcher. It is structured around the components defined in the `agent_architecture.md` and `implementation_plan.md`.

## 1. Input Parsing & Intent Routing
- **Vague or Incomplete Job Descriptions (JD):** The user provides a JD like "Looking for a software engineer" with no specific must-haves. *Handling:* The agent should recognize the lack of criteria and explicitly prompt the user for clarification before searching.
- **Ambiguous Natural Language Queries:** The user asks, "Who is the better one?" without specifying which candidates to compare. *Handling:* The `Intent_Router` must recognize missing context and ask for clarification ("Who would you like me to compare?").
- **Contradictory Human Feedback:** The user says "Focus only on React" and in the next turn says "Ignore React, just look for Python", but the original JD strictly required React. *Handling:* The agent must correctly overwrite the state's `extracted_requirements` to prioritize the latest human instruction while maintaining a log of the change.

## 2. Tool & Retrieval Failures
- **Empty RAG Search Results:** The `rag_search` tool returns 0 candidates that meet the extracted requirements (e.g., highly niche skills). *Handling:* Instead of crashing or passing an empty list to the screening node, the agent should report "No candidates found" and ask the user if they'd like to relax the requirements.
- **Corrupted or Unreadable Resumes:** `fs_tools` encounters an encrypted PDF, an image-only PDF without OCR, or a corrupted file. *Handling:* The tool should gracefully fail for that specific file, log the error, and continue processing the rest of the dataset.
- **Context Window Overflow:** If a candidate has a 10-page resume, or if the conversation history (`messages` in `AgentState`) becomes too long, the Groq LLM may exceed its token limit. *Handling:* Implement message summarization or context truncation within the `AgentState` before passing data to the LLM.

## 3. Screening & Reasoning (LLM Hallucinations)
- **Candidate Tie in Multi-Round Screening:** The LLM evaluates two candidates and gives them the exact same score or evaluation matrix. *Handling:* The system should explicitly highlight the tie in the `Generate_Report` node and rely on the recruiter (Human-in-the-loop) to break it.
- **Hallucinated Skills:** The `compare_candidates` tool invents a skill for a candidate that was not in their retrieved resume text. *Handling:* Use strict prompt engineering ("Base your analysis strictly on the provided text") and consider a verification step checking the final report against the raw text.
- **False 'Hire' Recommendations:** The agent recommends a "Hire" tag for a candidate who is missing a critical 'must-have' requirement. *Handling:* Implement a deterministic check (code-level rule) that prevents a "Hire" status if a must-have is missing, rather than relying solely on the LLM's subjective scoring.

## 4. Graph Execution & State Management
- **Infinite Graph Loops:** A poorly configured conditional edge causes the agent to bounce infinitely between `Search_Resumes` and `Parse_Requirements` without ever reaching the `Generate_Report` or `END` nodes. *Handling:* Implement a maximum recursion limit or turn counter in the `AgentState` to forcefully break the loop and return an error message to the user.
- **State Data Corruption:** One of the nodes accidentally overwrites the `jd_raw` or `messages` history instead of appending/updating correctly. *Handling:* Ensure nodes return only specific delta updates and utilize LangGraph's `add_messages` reducer to safely append data.
