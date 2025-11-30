from google.adk.a2a.utils.agent_to_a2a import to_a2a
from db_agent.db_agent import get_db_agent, DBAgentPlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from db_agent.db_agent import get_db_agent, DBAgentPlugin

import warnings
import os
from dotenv import load_dotenv
import sys

# You should run it using uvicorn (see README for more details)

# Check if Gemini API key is in .env
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print(
        f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to .env file"
    )
    sys.exit()

warnings.filterwarnings("ignore")

# Configure a2a connection
db_agent = get_db_agent()
session_service = InMemorySessionService()
db_runner = Runner(
    agent=db_agent,
    app_name="agents",
    session_service=session_service,
    plugins=[
        DBAgentPlugin(log_console=False)
    ]
)
a2a_app = to_a2a(db_agent, port=8001, runner=db_runner)