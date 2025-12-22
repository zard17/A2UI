
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
from .a2ui_schema import A2UI_SCHEMA

def get_selector_prompt() -> str:
    """
    Constructs the prompt for the decision step (Text vs UI vs Dynamic UI).
    """
    
    template_descriptions = []
    for key, value in TEMPLATES.items():
        template_descriptions.append(f"- {key}: {value['description']}")
    
    template_list_str = "\n".join(template_descriptions)

    return f"""
    You are an intelligent assistant that helps users with a variety of tasks.
    Your goal is to decide whether the user's request is best served by a text response, a pre-defined UI template, or a dynamically generated UI.

    AVAILABLE UI TEMPLATES:
    {template_list_str}

    INSTRUCTIONS:
    1. Analyze the user's request.
    2. detailed rules:
        - If the request matches a specific template use case:
            - Asking for a list/comparison -> 'UI' + 'SINGLE_COLUMN_LIST'
            - Asking to fill form -> 'UI' + 'FORM'
            - Confirmation -> 'UI' + 'CONFIRMATION'
            - Simple text/joke -> 'UI' + 'SIMPLE_MESSAGE'
        - If the request requires a rich interface but DOES NOT fit any of the above templates (e.g. "Create a dashboard", "Show a complex layout"), you MUST select 'DYNAMIC_UI'.
        - Only select 'TEXT' if it's an error or absolutely no UI is needed.
    
    OUTPUT FORMAT:
    You MUST output a valid JSON object with the following structure:
    {{
        "decision": "UI" or "DYNAMIC_UI" or "TEXT",
        "template_id": "TEMPLATE_NAME" (if decision is UI, otherwise null),
        "reason": "Brief explanation of your decision"
    }}
    """

def get_generator_prompt(template_id: str = None, is_dynamic: bool = False) -> str:
    """
    Constructs the prompt for generating the final response.
    """
    
    if is_dynamic:
        return f"""
        You are an advanced UI design assistant. Your goal is to generate a dynamic A2UI interface strictly following the schema.

        You MUST follow these rules:
        1.  Your response MUST be in two parts, separated by the delimiter: `---a2ui_JSON---`.
        2.  The first part is your conversational text response explaining what you built.
        3.  The second part must be a list of A2UI messages.
        4.  You MUST include a `beginRendering` message to initialize the surface.
        5.  You MUST include a `surfaceUpdate` message to define the components.
        6.  Example structure: `[ {{ "beginRendering": ... }}, {{ "surfaceUpdate": {{ "surfaceId": ..., "components": ... }} }} ]`
        7.  You are free to design the UI using Rows, Columns, Cards, Text, Images, etc., as defined in the schema.

        --- A2UI JSON SCHEMA ---
        {A2UI_SCHEMA}
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
    
    - Ensure the JSON part allows the A2UI spec (implicitly followed by using the template).
    - CRITICAL: Parsing is strict. You MUST escape all double quotes and newlines within the `valueString` fields. Use `\\n` for newlines and `\\\"` for quotes.
    """
