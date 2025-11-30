from google.adk.agents import BaseAgent, Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk.tools import AgentTool
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)

import os
import logging
from typing import Optional

class BookshopAgentPlugin(BasePlugin):
    def __init__(self, log_level=logging.INFO, log_console=True) -> None:
        super().__init__(name="bookshop_agent_plugin")
        os.makedirs("logs", exist_ok=True)

        self.logger = logging.getLogger("bookshop_agent_logger")
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            log_file_handler = logging.FileHandler("logs/bookshop_agent_logs.log")
            handlers = [log_file_handler]

            if log_console:
                console_handler = logging.StreamHandler()
                handlers.append(console_handler)

            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s"
            )

            for handler in handlers:
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

    async def before_run_callback(
      self, 
      *, 
      invocation_context: InvocationContext
    ) -> None:
        self.logger.info(f"[BookshopAgentPlugin] Agent {invocation_context.agent.name} started answering.")

    async def after_run_callback(
      self, 
      *, 
      invocation_context: InvocationContext
    ) -> None:
        self.logger.info(f"[BookshopAgentPlugin] Agent {invocation_context.agent.name} returned the answer.")


def get_bookshop_agent():
    remote_db_agent = RemoteA2aAgent(
        name="db_agent",
        description="Remote agent that queries the BOOKS database for titles matching the user's request.",
        agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    search_agent = Agent(
        name="search_agent",
        model=Gemini(
            model="gemini-2.5-flash-lite", 
            retry_options=types.HttpRetryOptions(
                attempts=5, 
                exp_base=7,  
                initial_delay=1,
                http_status_codes=[429, 500, 503, 504]
            )
        ),
        description="Agent that receives user request, modifies it using memory, and delegates the query to db_agent.",
        instruction="""
        You are a bookshop search assistant.

        Task:
        1. Use session memory to modify the user’s original request.
           Example: if earlier the user said they dislike politics, add this as a constraint.
        2. Call db_agent with the modified search prompt.
        3. Return your final output in this format:

           Books search: <result returned by db_agent>
           User prompt: <original user prompt>

        Important rule:
        - Only modify the prompt using things the user *dislikes*.
          Do NOT add things the user likes or was searching beforehand to the modified query.

        Guidelines:
        - Start the search immediately after receiving a request.
        - Never ask the user for clarification.
        """,
        tools=[AgentTool(remote_db_agent)],
        output_key="book_search",
    )

    recommend_agent = Agent(
        name="recommend_agent",
        model=Gemini(
            model="gemini-2.5-flash-lite",
            retry_options=types.HttpRetryOptions(
                attempts=5, 
                exp_base=7,  
                initial_delay=1,
                http_status_codes=[429, 500, 503, 504]
            )
        ),
        description="Agent that selects top book recommendations.",
        instruction="""
        You are a book recommendation assistant.

        Your input is stored in {book_search}, containing:
        - The books returned by db_agent
        - The original user prompt

        Task:
        - If no books are returned by db_agent, say that the search was unsuccessful 
          and ask the user if they need help with something else.
        - Select up to 5 books that best match the user's criteria. 
          You may return fewer than 5 or even 0 if none meet the criteria.
        - If after selection no books remain, say that the search was unsuccessful 
          and ask the user if they need help with something else.

        If at least one book is selected, return the results in EXACTLY this format:

          The search was successful. Here are the books I recommend:
          Title: <title>
          Authors: <authors>
          Category: <category>
          Summary: <30-word summary>
          Publisher: <publisher>
          Price: <price>
          Publication Year: <year>
          
        - Separate each book with one blank line.
        """,
        output_key="book_search_response",
    )

    bookshop_agent = SequentialAgent(
        name="book_search_agent_system",
        sub_agents=[search_agent, recommend_agent],
    )

    return bookshop_agent
