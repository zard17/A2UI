# Improvement Plan: Automated Template Generation ("Template Factory")

## Goal
Rapidly expand the library of available UI templates from ~10 to 100+ to fully leverage the Template Search System.

## Problem
Manually writing JSON templates is slow, error-prone, and tedious. To make the "Search System" effective, we need a high volume of diverse, high-quality A2UI patterns.

## Proposed Solution
Create a "Template Factory" script that uses an LLM to generate valid A2UI templates offline.

### 1. Taxonomy Definition
Define a list of categories to ensure diversity:
-   **Dashboards** (Financial, Health, Server, Analytics)
-   **Lists/Directories** (Contacts, Products, Movies, Files)
-   **Multimedia** (Video Player, Audio Player, Image Gallery)
-   **Forms** (Login, Signup, Survey, Feedback, Checkout)
-   **Social** (Profile, Post, Comment Thread, Chat)
-   **Articles** (News, Blog, Documentation, FAQ)

### 2. Generator Script (`generate_templates.py`)
-   **Input**: A topic or category name.
-   **Prompt**: "Generate a valid A2UI `surfaceUpdate` JSON template for a [Topic] interface. Use placeholders like `{{title}}` or `{{image_url}}` for dynamic data."
-   **Validation**:
    -   Validate generated JSON against `A2UI_SCHEMA`.
    -   Check for "hallucinated" components.
    -   Auto-fix common errors.
-   **Output**: Save valid templates to `generic_chat/templates/` directory (one JSON file per template).

### 3. Metadata Extraction
-   For each generated template, ask the LLM to generate:
    -   A short **Description** (e.g., "A dark-mode analytics dashboard with 3 charts").
    -   **Keywords** (e.g., "finance", "chart", "dark").
-   Save this metadata alongside the JSON (e.g., in a `manifest.json` or `index.json`) for the Search System to use.

## Workflow
1.  **Run Factory**: `python generate_templates.py --count 50`
2.  **Human Review**: (Optional) Quickly scan generated templates in a viewer.
3.  **Indexing**: Run the Search System indexer to ingest the new templates.
