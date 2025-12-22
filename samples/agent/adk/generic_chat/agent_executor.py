
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

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_parts_message,
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from a2ui.a2ui_extension import create_a2ui_part, try_activate_a2ui_extension
from .agent import GenericChatAgent

logger = logging.getLogger(__name__)


class GenericChatAgentExecutor(AgentExecutor):
    """Generic Chat AgentExecutor."""

    def __init__(self, base_url: str):
        self.agent = GenericChatAgent(base_url=base_url)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = ""
        ui_event_part = None

        logger.info(
            f"--- Client requested extensions: {context.requested_extensions} ---"
        )
        try_activate_a2ui_extension(context)

        # Parse the incoming message
        if context.message and context.message.parts:
            for part in context.message.parts:
                if isinstance(part.root, DataPart):
                    if "userAction" in part.root.data:
                        ui_event_part = part.root.data["userAction"]
                        break # Found the UI event
                elif isinstance(part.root, TextPart):
                    query = part.root.text

        if ui_event_part:
            logger.info(f"Received a2ui ClientEvent: {ui_event_part}")
            action = ui_event_part.get("actionName")
            ctx = ui_event_part.get("context", {})
            # Generic conversion of event to text
            query = f"User performed action: '{action}' with data: {json.dumps(ctx)}"
        elif not query:
            # Fallback if no text part
             query = context.get_user_input()

        logger.info(f"--- AGENT_EXECUTOR: Final query for LLM: '{query}' ---")

        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # Reuse session_id from task.context_id
        async for item in self.agent.stream(query, task.context_id):
            is_task_complete = item["is_task_complete"]
            if not is_task_complete:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(item["updates"], task.context_id, task.id),
                )
                continue

            # Assuming single turn for simplicity in this PoC
            final_state = TaskState.completed 
            
            content = item["content"]
            final_parts = []
            if "---a2ui_JSON---" in content:
                logger.info("Splitting final response into text and UI parts.")
                text_content, json_string = content.split("---a2ui_JSON---", 1)

                if text_content.strip():
                    final_parts.append(Part(root=TextPart(text=text_content.strip())))

                if json_string.strip():
                    logger.info(f"Raw UI JSON received: {json_string}")
                    try:
                        json_string_cleaned = (
                            json_string.strip().lstrip("```json").rstrip("```").strip()
                        )
                        json_data = json.loads(json_string_cleaned)

                        if isinstance(json_data, list):
                            for message in json_data:
                                # Auto-fix for common LLM error: missing wrapper key for surfaceUpdate
                                if "surfaceId" in message and "components" in message and "surfaceUpdate" not in message:
                                    logger.warning("Auto-fixing malformed surfaceUpdate message (missing wrapper)")
                                    message = {"surfaceUpdate": message}
                                final_parts.append(create_a2ui_part(message))
                        else:
                            final_parts.append(create_a2ui_part(json_data))

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse UI JSON: {e}")
                        final_parts.append(Part(root=TextPart(text=json_string)))
            else:
                final_parts.append(Part(root=TextPart(text=content.strip())))

            await updater.update_status(
                final_state,
                new_agent_parts_message(final_parts, task.context_id, task.id),
                final=True, # Mark as final
            )
            break

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
