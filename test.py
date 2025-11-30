from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.invocation_context import InvocationContext

import warnings
import os
from dotenv import load_dotenv
import sys

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print(
        f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to .env file"
    )
    sys.exit()