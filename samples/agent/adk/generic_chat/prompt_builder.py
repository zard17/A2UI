
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .templates import TEMPLATES

# The A2UI schema remains constant for all A2UI responses.
# We include a minimal version here or reuse the one from other samples if available.
# For simplicity and self-containment, I will define the schema here, 
# ensuring it matches the v0.8 spec we saw in the restaurant finder sample.

A2UI_SCHEMA = r'''
{
  "title": "A2UI Message Schema",
  "type": "object",
  "properties": {
    "beginRendering": { "type": "object", "required": ["root", "surfaceId"] },
    "surfaceUpdate": {
      "type": "object",
      "required": ["surfaceId", "components"],
      "properties": {
        "components": {
           "type": "array",
           "items": { "type": "object", "required": ["id", "component"] }
        }
      }
    },
    "dataModelUpdate": {
      "type": "object",
      "required": ["contents", "surfaceId"],
      "properties": {
         "contents": { "type": "array" }
      }
    }
  }
}
'''

def get_selector_prompt() -> str:
    """
    Constructs the prompt for the decision step (Text vs UI).
    """
    
    template_descriptions = []
    for key, value in TEMPLATES.items():
        template_descriptions.append(f"- {key}: {value['description']}")
    
    template_list_str = "\n".join(template_descriptions)

    return f"""
    You are an intelligent assistant that helps users with a variety of tasks.
    Your goal is to decide whether the user's request is best served by a simple text response or a rich UI response.

    AVAILABLE UI TEMPLATES:
    {template_list_str}

    INSTRUCTIONS:
    1. Analyze the user's request.
    2. detailed rules:
        - If the request asks for a list, comparison, or structured data (e.g. "show me", "list", "top 5"), choose 'UI' and the 'SINGLE_COLUMN_LIST' template.
        - If the request implies filling out information (e.g. "sign up", "register", "contact form"), choose 'UI' and the 'FORM' template.
        - If the request is a confirmation of a previous action, choose 'UI' and the 'CONFIRMATION' template.
        - If the user's request is best served by a simple text answer (e.g. "tell me a joke", "who are you"), you MUST select 'UI' and use the 'SIMPLE_MESSAGE' template.
        - You should almost ALWAYS select 'UI'. Only select 'TEXT' if you absolutely cannot fit the response into any template (which shouldn't happen).
    
    OUTPUT FORMAT:
    You MUST output a valid JSON object with the following structure:
    {{
        "decision": "UI" or "TEXT",
        "template_id": "TEMPLATE_NAME" (if decision is UI, otherwise null),
        "reason": "Brief explanation of your decision"
    }}
    """

def get_generator_prompt(template_id: str = None) -> str:
    """
    Constructs the prompt for generating the final response.
    """
    
    if not template_id or template_id not in TEMPLATES:
        # Fallback to generic text agent if no valid template
        return """
        You are a helpful assistant. Please respond to the user's request with a clear and concise text response.
        """
    
    selected_template = TEMPLATES[template_id]["json"]
    
    return f"""
    You are a helpful assistant. Your goal is to generate a response using a specific UI template.

    You MUST follow these rules:
    1.  Your response MUST be in two parts, separated by the delimiter: `---a2ui_JSON---`.
    2.  The first part is your conversational text response.
    3.  The second part is a return of the "UI TEMPLATE" provided below, but with the `dataModelUpdate` populated with the actual content relevant to the user's request.
    
    --- UI TEMPLATE (Use this structure) ---
    {selected_template}
    
    --- DATA MODEL INSTRUCTIONS ---
    - You must fill in the `valueString`, `valueNumber`, etc. in the `dataModelUpdate` section of the template.
    - Do NOT change the `surfaceUpdate` or `beginRendering` sections unless absolutely necessary, stick to the data model.
    - Example: If the template has a key "title", set its value to a relevant title for the user's query.
    
    Ensure the JSON part allows the A2UI spec (implicitly followed by using the template).
    """
