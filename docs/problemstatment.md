# Problem Statement & Project Context

## Project Context
This project is an **AI-Powered Resume Matcher and Assistant** designed to streamline and automate the recruitment and candidate screening process. It builds upon previous developmental milestones, including:
- **Milestone 1 (File Assistant):** Processing and standardizing various resume file formats (PDF, DOCX, TXT).
- **Milestone 2 (RAG Pipeline):** Developing a Retrieval-Augmented Generation (RAG) system using Groq and HuggingFace for semantic search and candidate data retrieval.

The current phase focuses on elevating the system from a simple retrieval pipeline to an **Agentic Workflow** using LangGraph. This workflow is capable of complex reasoning, multi-step execution, and interactive user conversations.

## Problem Statement
Recruiters and hiring managers spend an excessive amount of time manually reviewing hundreds of resumes for a single job opening. Traditional keyword-based Applicant Tracking Systems (ATS) often miss highly qualified candidates who use different terminology, while manual screening is slow, unscalable, and prone to human bias. 

There is a critical need for an intelligent, context-aware system that can:
1. Deeply understand job requirements (must-haves vs. nice-to-haves).
2. Semantically evaluate and compare candidate profiles against these requirements.
3. Provide transparent, explainable reasoning for its rankings and recommendations.
4. Interact with recruiters dynamically to refine criteria and answer specific queries about candidates.

The goal is to build a conversational AI agent that acts as a virtual hiring assistant, capable of multi-round screening and providing actionable insights to empower human decision-makers.

---

## Assignment Requirements
Part A: Agent Architecture (40%)

Create matching_agent.py using LangGraph:

Agent State Design

Track conversation history

Maintain job requirements understanding

Store candidate shortlist and reasoning

Agent Workflow (Graph Structure)
START → Parse JD → Extract Requirements → Search Resumes → 

Rank Candidates → Generate Report → Human Feedback Loop → END

Tools Available to Agent

All file system tools (from Milestone 1)

RAG search tool (from Milestone 2)

Additional tools:

extract_requirements(jd: str) - Parse must-have vs nice-to-have

compare_candidates(candidate_ids: list) - Head-to-head comparison

generate_interview_questions(candidate_id: str) - Create screening questions

Part B: Interactive Features (30%)

Conversational Interface

Accept natural language queries

“Find me candidates with React and 3+ years experience”

“Compare the top 3 matches side by side”

“Why did John rank higher than Jane?”

Iterative Refinement

Allow users to adjust requirements mid-conversation

Agent re-ranks based on new criteria

Explains changes in rankings

Part C: Advanced Capabilities (30%)

Multi-Round Screening

Initial screen: top 10 from 100 resumes

Second round: deep analysis of top 10

Final round: generate hire/no-hire recommendation

Explainability

Generate detailed match reports

Highlight strengths and gaps for each candidate

Provide improvement suggestions for borderline candidates

Submission guidelines
LangGraph-based agent implementation

State machine diagram (visual representation)

Chat interface (CLI or Streamlit/Gradio)

Test scenarios: 5+ conversation flows

Demo video (5-6 minutes) showing agent reasoning