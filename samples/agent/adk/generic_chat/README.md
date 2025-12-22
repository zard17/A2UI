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

## Sample Queries

Here are tested queries you can try with the agent:

### Text Response
*Maps to `SIMPLE_MESSAGE` template.*

-   "Tell me a joke."
-   "Who are you?"
-   "What is the capital of Japan?"
-   "Hello, how are you today?"
-   "Explain the theory of relativity in one sentence."
-   "Write a haiku about debugging."
-   "What is 25 * 4?"
-   "Give me a motivational quote."
-   "What implies 'dynamic UI' in this project?"
-   "Summarize the history of the internet."

### Predefined UI Templates
*Triggered when request matches specific structures like Lists, Forms, or Confirmations.*

-   **List**: "Top 5 highest mountains in the world."
-   **List**: "Show me a list of healthy snacks."
-   **List**: "Recommend 3 movies for a rainy day."
-   **List**: "Compare the features of Python and JavaScript."
-   **Form**: "I want to sign up for the newsletter."
-   **Form**: "Open a registration form for a new user."
-   **Form**: "Create a support ticket."
-   **Confirmation**: "I have finished reading the document."
-   **Confirmation**: "Confirm that the data has been saved."
-   **Confirmation**: "Mark this task as complete."

### Dynamic UI
*Triggered when the request implies a complex or custom layout that doesn't fit a standard template.*

-   **Dashboard**: "Create a dashboard showing server health with a chart and status indicators."
-   **Profile**: "Design a user profile page with a circular avatar, bio text, and a grid of recent photos."
-   **E-commerce**: "Show me a product page for a pair of sneakers with a large main image, price tag, size selector, and a 'Buy Now' button."
-   **Weather**: "Build a weather forecast view with a large current temperature, an icon for conditions, and a horizontal scroll of hourly forecasts."
-   **Media**: "Create a music player interface with album art, a progress slider, and playback control buttons."
-   **Kanban**: "Show a task board with three columns: 'To Do', 'Doing', and 'Done', with a few generic cards in each."
-   **Recipe**: "Display a recipe card for pancakes with a hero image at the top, ingredients listed on the left, and instructions on the right."
-   **Settings**: "Create a settings menu with a 'Dark Mode' toggle, a 'Notifications' checkbox, and a 'Save' button."
-   **News**: "Design a news feed with one large headline story at the top and three smaller list items below it."
-   **Login**: "Make a login screen with a logo at the top, email and password fields, and a 'Forgot Password' link at the bottom."
