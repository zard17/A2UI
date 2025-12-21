
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

import logging
import os

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2ui.a2ui_extension import get_a2ui_agent_extension
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

from .agent import GenericChatAgent
from .agent_executor import GenericChatAgentExecutor

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=10003) # Using a new port to avoid conflict
def main(host, port):
    # Check for API key (simplistic check for PoC)
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE":
        logger.warning("WARNING: GEMINI_API_KEY is not set. The agent will fail at runtime unless using Vertex AI.")

    capabilities = AgentCapabilities(
        streaming=True,
        extensions=[get_a2ui_agent_extension()],
    )
    skill = AgentSkill(
        id="chat",
        name="Generic Chat",
        description="A generic chat skill that shows UIs triggered by query analysis.",
        tags=["chat", "generic"],
        examples=["Tell me a joke", "Top 5 mountains", "Sign up form"],
    )

    base_url = f"http://{host}:{port}"

    agent_card = AgentCard(
        name="Generic Chat Agent",
        description="Dynamic UI Chat Agent",
        url=base_url,
        version="1.0.0",
        default_input_modes=GenericChatAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=GenericChatAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )

    agent_executor = GenericChatAgentExecutor(base_url=base_url)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    app = server.build()

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://localhost:\d+", # Allow any localhost port for clients
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info(f"Starting generic chat agent on ported {port}...")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
