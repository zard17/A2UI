# Generic A2UI Chat Agent

This is a Proof of Concept (PoC) for a generic chat agent that uses A2UI to dynamically render rich UI responses based on the user's query.

## Capabilities

The agent can handle various types of queries and select the most appropriate UI template:

-   **Casual Conversation**: "Tell me a joke", "Who are you?" -> Renders a simple text card.
-   **Lists**: "Top 5 movies", "Search results for pizza" -> Renders a list of items with images and details.
-   **Forms**: "Sign up for newsletter", "Book a table" -> Renders an interactive form.
-   **Weather**: "What's the weather today?" -> Renders a weather forecast card.
-   **Articles/Info**: "Tell me about quantum computing" -> Renders an article layout with an image and detailed text.

## How it works

1.  **Selector**: An LLM analyzes the user's query to decide whether to use a UI template or plain text (which is also wrapped in a UI).
2.  **Generator**: An LLM generates the final A2UI JSON response using the selected template.
3.  **Renderer**: The client (e.g., Web, iOS) renders the A2UI JSON into native UI components.

## Running the Agent

```bash
export GEMINI_API_KEY=<your-api-key>
python -m A2UI.samples.agent.adk.generic_chat
```
