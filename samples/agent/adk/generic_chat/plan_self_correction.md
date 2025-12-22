# Improvement Plan: Self-Correction Loop for JSON Generation

## Goal
Ensure the Generic Chat agent always returns valid, schema-compliant A2UI JSON, even when the LLM makes syntax errors or hallucinations.

## Problem
LLMs are probabilistic. Even with perfect prompts, they occasionally produce:
-   **Syntax Errors**: Unescaped quotes, trailing commas.
-   **Schema Violations**: Missing required fields (e.g., `components`), missing wrappers (like the `surfaceUpdate` issue we debugged).
-   **Hallucinations**: Using non-existent component types.

## Proposed Solution
Implement a **Validator-Feedback Loop** (also known as "Reflexion").

### Current Flow
`User Query -> LLM -> JSON -> Client`

### Improved Flow with Correction
1.  **Generation**: LLM produces `draft_json`.
2.  **Validation**:
    -   **Step A**: Use `json.loads()` to check basic syntax.
    -   **Step B**: Use `jsonschema.validate(draft_json, A2UI_SCHEMA)` to check strict adherence to spec.
3.  **Decision**:
    -   **If Valid**: Return to Client.
    -   **If Invalid**: Enter Correction Mode.
4.  **Correction (Retry)**:
    -   Construct a **Error Prompt**:
        > "The JSON you generated was invalid properly.
        > Error: [Error Message from Validator]
        > Your Output: [draft_json]
        > Task: Fix the JSON and output ONLY the valid JSON."
    -   Send this back to the LLM (same session).
    -   Repeat up to `MAX_RETRIES` (e.g., 3).
5.  **Fallback**: If strict validation still fails after retries, return a safe "Error UI" or plain text to the user instead of crashing the server.

## Implementation Steps
1.  **Validator**: Enhance `agent_executor.py` or `agent.py` to import `jsonschema`.
2.  **Loop Logic**: Convert the single `generator_runner.run_async` call into a `while` loop keeping track of `attempts`.
3.  **Error Handling**: specifically catch `json.JSONDecodeError` and `jsonschema.ValidationError`.
4.  **Prompting**: Create `get_correction_prompt(error_msg, original_output)` in `prompt_builder.py`.
