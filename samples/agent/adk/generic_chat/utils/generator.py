import json
import logging
import os
import re
import litellm
from ..a2ui_schema import A2UI_SCHEMA

logger = logging.getLogger(__name__)

class TemplateGenerator:
    def __init__(self, model_name: str = None):
        # Default to the same model as the agent or a strong logical model
        self.model_name = model_name or os.getenv("LITELLM_MODEL", "gemini/gemini-2.0-flash-exp")

    def generate(self, topic: str) -> dict:
        """
        Generates a UI template for the given topic.
        Returns a dict with 'id', 'description', 'keywords', and 'json' (string).
        """
        logger.info(f"Generating template for topic: {topic}")
        
        prompt = f"""
        You are an expert UI designer and A2UI protocol specialist.
        Your goal is to create a reusable, high-quality A2UI JSON template for a "{topic}" interface.

        Your output MUST be a valid JSON object with the following structure:
        {{
            "id": "A unique, uppercase identifier (e.g., FITNESS_DASHBOARD)",
            "description": "A short, descriptive summary of what this template does.",
            "keywords": "A comma-separated string of relevant keywords for search.",
            "template_json": "THE_ACTUAL_A2UI_JSON_STRING" 
        }}

        INSTRUCTIONS FOR 'template_json':
        1. It must be a valid JSON LIST containing `beginRendering`, `surfaceUpdate`, and `dataModelUpdate`.
        2. It MUST validate against the A2UI Schema provided below.
        3. Use placeholders like `{{{{title}}}}` or `{{{{image_url}}}}` for dynamic content in the `dataModelUpdate` section.
        4. The `surfaceUpdate` MUST use `dataBinding` where appropriate to link to the data model.
        5. IMPORTANT: The `template_json` field must be a STRING containing the escaped JSON of the A2UI messages.

        --- A2UI SCHEMA ---
        {A2UI_SCHEMA}
        """

        try:
            response = litellm.completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            
            # Extract JSON from markdown code block if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            data = json.loads(content)
            
            # Basic validation of the inner JSON string
            try:
                inner_json = json.loads(data["template_json"])
                # Simple check for required message types
                types = [list(msg.keys())[0] for msg in inner_json]
                if "beginRendering" not in types or "surfaceUpdate" not in types:
                    logger.warning(f"Generated template for {topic} missing standard messages: {types}")
            except json.JSONDecodeError:
                logger.error(f"Generated template_json for {topic} is not valid JSON string.")
                return None

            return data

        except Exception as e:
            logger.error(f"Failed to generate template for {topic}: {e}")
            return None
