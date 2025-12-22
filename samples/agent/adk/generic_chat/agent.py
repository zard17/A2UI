
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

import json
import logging
import os
from collections.abc import AsyncIterable
from typing import Any

from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .prompt_builder import get_generator_prompt, get_selector_prompt
from .utils.searcher import TemplateSearcher

logger = logging.getLogger(__name__)


class GenericChatAgent:
    """An agent that dynamically selects UI templates based on user query."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._user_id = "generic_agent_user"
        
        # We will spin up a fresh runner/agent for each turn in this PoC to strictly separate instructions
        # calling it "multi-turn within one request" style
        # We will spin up a fresh runner/agent for each turn in this PoC to strictly separate instructions
        # calling it "multi-turn within one request" style
        self.model_name = os.getenv("LITELLM_MODEL", "gemini/gemini-2.0-flash-exp")
        
        # Initialize the searcher (computes embeddings on startup)
        try:
            self.searcher = TemplateSearcher(model_name=os.getenv("EMBEDDING_MODEL", "gemini/text-embedding-004"))
        except Exception as e:
            logger.error(f"Failed to initialize TemplateSearcher: {e}")
            self.searcher = None

    def _create_runner(self, instruction: str) -> Runner:
        agent = LlmAgent(
            model=LiteLlm(model=self.model_name),
            name="generic_chat_agent",
            description="A generic agent.",
            instruction=instruction,
            tools=[], # No extra tools for this simple PoC, but could add search etc.
        )
        return Runner(
            app_name=agent.name,
            agent=agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def stream(self, query, session_id) -> AsyncIterable[dict[str, Any]]:
        logger.info(f"--- Processing query: {query} ---")
        
        # Step 1: Decision (UI vs Text)
        
        # 1.1 Search for relevant templates
        candidate_templates = None
        if self.searcher:
            candidate_templates = self.searcher.search(query)
            
        selector_prompt = get_selector_prompt(candidate_templates)
        selector_runner = self._create_runner(instruction=selector_prompt)
        
        # Create session for selector
        selector_session_id = f"{session_id}_selector"
        await selector_runner.session_service.create_session(
            app_name=selector_runner.agent.name,
            user_id=self._user_id,
            session_id=selector_session_id
        )

        decision_message = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        
        decision_response_text = ""
        decision_response_text = ""
        try:
            async for event in selector_runner.run_async(
                user_id=self._user_id, session_id=selector_session_id, new_message=decision_message
            ):
                 if event.is_final_response() and event.content:
                    decision_response_text = "\n".join([p.text for p in event.content.parts if p.text])
        except Exception as e:
            logger.error(f"Selector LLM failed: {e}")
            yield {
                "is_task_complete": True,
                "content": f"I'm sorry, I'm having trouble connecting to my brain right now (Rate Limit or Error). Please try again in 30 seconds.\n\n---a2ui_JSON---\n```json\n[\n  {{ \"beginRendering\": {{ \"surfaceId\": \"main\", \"root\": \"root-column\" }} }},\n  {{ \"surfaceUpdate\": {{\n    \"surfaceId\": \"main\",\n    \"components\": [\n      {{ \"id\": \"root-column\", \"component\": {{ \"Column\": {{ \"children\": {{ \"explicitList\": [\"message-card\"] }} }} }} }},\n      {{ \"id\": \"message-card\", \"component\": {{ \"Card\": {{ \"child\": \"message-text\" }} }} }},\n      {{ \"id\": \"message-text\", \"component\": {{ \"Text\": {{ \"text\": {{ \"literal\": \"I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a few moments.\" }} }} }} }}\n    ]\n  }} }}\n]\n```"
            }
            return

        logger.info(f"--- Selector Decision: {decision_response_text} ---")
        
        decision_data = {}
        try:
            # Clean up potential markdown code blocks
            clean_json = decision_response_text.strip().removeprefix("```json").removesuffix("```").strip()
            decision_data = json.loads(clean_json)
        except json.JSONDecodeError:
            logger.error("Failed to parse selector decision JSON. Fallback to TEXT.")
            decision_data = {"decision": "TEXT"}

        # Step 2: Generation
        template_id = decision_data.get("template_id")
        decision = decision_data.get("decision", "TEXT")
        
        is_dynamic = (decision == "DYNAMIC_UI")
        
        if not is_dynamic and not template_id:
             # Default fallback if regular UI but missing ID
             template_id = "SIMPLE_MESSAGE"

        generator_prompt = get_generator_prompt(template_id, is_dynamic=is_dynamic)
        generator_runner = self._create_runner(instruction=generator_prompt)
        
        # Create session for generator
        generator_session_id = f"{session_id}_generator"
        await generator_runner.session_service.create_session(
            app_name=generator_runner.agent.name,
            user_id=self._user_id,
            session_id=generator_session_id
        )
        
        # Pass the original query to the generator
        generator_message = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        
        try:
            async for event in generator_runner.run_async(
                user_id=self._user_id, session_id=generator_session_id, new_message=generator_message
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_content = "\n".join([p.text for p in event.content.parts if p.text])
                        yield {
                            "is_task_complete": True,
                            "content": final_content,
                        }
                else:
                    yield {
                        "is_task_complete": False,
                        "updates": "Thinking...",
                    }
        except Exception as e:
            logger.error(f"Generator LLM failed: {e}")
            yield {
                "is_task_complete": True,
                "content": f"I'm sorry, I encountered an error generating the response (Rate Limit or Error). Please try again later.\n\n---a2ui_JSON---\n```json\n[\n  {{ \"beginRendering\": {{ \"surfaceId\": \"main\", \"root\": \"root-column\" }} }},\n  {{ \"surfaceUpdate\": {{\n    \"surfaceId\": \"main\",\n    \"components\": [\n      {{ \"id\": \"root-column\", \"component\": {{ \"Column\": {{ \"children\": {{ \"explicitList\": [\"message-card\"] }} }} }} }},\n      {{ \"id\": \"message-card\", \"component\": {{ \"Card\": {{ \"child\": \"message-text\" }} }} }},\n      {{ \"id\": \"message-text\", \"component\": {{ \"Text\": {{ \"text\": {{ \"literal\": \"I'm sorry, I'm having trouble generating the response right now. Please try again in a few moments.\" }} }} }} }}\n    ]\n  }} }}\n]\n```"
            }

