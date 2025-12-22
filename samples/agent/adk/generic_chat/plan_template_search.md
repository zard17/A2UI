# Improvement Plan: Template Search System

## Goal
Scale the Generic Chat agent from supporting ~10 templates to 100+ templates without overwhelming the LLM's context window or degrading decision accuracy.

## Problem
Currently, `prompt_builder.py` injects **all** template descriptions into the selector prompt.
-   **Token Usage**: Linearly increases with template count.
-   **Accuracy**: Too many choices confuse the LLM (Choice Paralysis).
-   **Latency**: Longer prompt processing.

## Proposed Solution
Implement a **Retrieval-Augmented Generation (RAG)** step for template selection.

### 1. Indexing (Offline/Startup)
-   Create a lightweight index of all available templates in `templates.py`.
-   **Method A (Simple)**: TF-IDF / BM25 keyword matching on template `description` and `keywords`.
-   **Method B (Semantic)**: Use a lightweight embedding model (e.g., `all-MiniLM-L6-v2`) to embed template descriptions into a local Vector Store (e.g., `chromadb` or even an in-memory numpy array for <1000 items).

### 2. Retrieval (Runtime)
-   **Step**: Before generating the `selector_prompt` in `agent.py`.
-   **Input**: User's raw query (e.g., "Show me apple's stock price").
-   **Process**:
    -   Embed/Process query.
    -   Search index for Top-K most relevant templates (e.g., K=5).
    -   *Example Result*: `['STOCK_CHART', 'NUMBER_CARD', 'NEWS_LIST']`.

### 3. Prompt Construction
-   Modify `get_selector_prompt` to accept `candidate_templates`.
-   **Only** inject the descriptions for the Top-K candidates.
-   **Always** inject the `SIMPLE_MESSAGE` (Text) fallback.

## Implementation Steps
1.  **Dependencies**: Add `chromadb` or `scikit-learn` (for cosine sim) to `pyproject.toml`.
2.  **Metadata**: Enhance `TEMPLATES` in `templates.py` with `keywords` or richer `descriptions`.
3.  **Searcher Class**: Create `TemplateSearcher` in `generic_chat/utils/searcher.py`.
4.  **Integration**: Update `GenericChatAgent.stream()` to call `searcher.query(user_text)` before building the prompt.
