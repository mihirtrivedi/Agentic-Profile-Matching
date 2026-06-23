# Phase 6: 5+ Distinct Conversational Flows for Testing

Run these scenarios through the Streamlit UI to validate the state management, routing, and explainability of the agent.

## Flow 1: Standard Screening (The Happy Path)
1. **User:** Pastes a standard Job Description (e.g., "We need a Senior Python Developer with 5+ years experience. Must have FastAPI and Docker. Nice to have: Kubernetes and AWS.")
2. **Agent:** Extracts requirements, searches RAG vector store, runs deep comparison on top candidates, and returns a markdown report with Hire/No-Hire statuses.
3. **Validation:** Check if the JSON extraction worked correctly and if the agent successfully output the comparative matrix.

## Flow 2: Mid-Stream Requirement Refinement
1. **User:** Pastes the JD from Flow 1. Wait for the report.
2. **User:** "Actually, we don't need FastAPI anymore, but they absolutely MUST have Kubernetes."
3. **Agent:** Updates the `extracted_requirements` in the state, re-runs the search with the new criteria, and outputs a *new* report.
4. **Validation:** Ensure the agent didn't ask for a new JD, and verify the new report heavily weights Kubernetes over FastAPI.

## Flow 3: Explainability & Reasoning Verification
1. **User:** Pastes a JD for a Data Scientist (Must have: Python, SQL, Machine Learning). Wait for the report.
2. **User:** "Why did Candidate X receive a 'No-Hire' tag?"
3. **Agent:** Bypasses the RAG search, pulls from the `current_analysis` dictionary, and explains that Candidate X lacked SQL experience based on the comparative matrix.
4. **Validation:** Ensure the agent's response is directly based on the generated reasoning trace and that it correctly routes to `chat_response_node`.

## Flow 4: Generating Actionable Interview Questions
1. **User:** Run standard screening for a Frontend Dev (Must have: React, TypeScript). Wait for report.
2. **User:** "Generate 3 interview questions for Candidate Y to test their weaknesses."
3. **Agent:** Analyzes Candidate Y's gaps (e.g., they had React but no TypeScript) and returns highly specific questions probing those gaps.
4. **Validation:** Check if the questions are tailored to the candidate's *missing* skills rather than generic behavioral questions.

## Flow 5: Handling Ambiguous / Unrelated Queries
1. **User:** "What is the capital of France?" OR "Who is better?" (without specifying candidates).
2. **Agent:** Routes to the chat node. Because the prompt restricts the agent to answer based *only* on the current screening context, it should politely refuse or ask for clarification regarding the candidates.
3. **Validation:** Ensure the agent does not hallucinate an answer outside of the recruiting context.
