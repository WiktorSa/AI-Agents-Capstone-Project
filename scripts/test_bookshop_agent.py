from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH

from booskshop_agent.bookshop_agent import get_bookshop_agent, BookshopAgentPlugin

import os
import sys
import asyncio
import warnings
from dotenv import load_dotenv
import requests

async def main():
    # Check if Gemini API key is in .env
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print(
            f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to .env file"
        )
        sys.exit()

    # Test if the Remote DB Agent server is running before doing any operations
    try:
        response = requests.get(
            f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}", timeout=5
        )

        if response.status_code != 200:
            print(f"❌ Failed to fetch agent card: {response.status_code}")
            print("Make sure the Remote DB Agent server is running (see README for more info)")
            sys.exit()

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching agent card: {e}")
        print("Make sure the Remote DB Agent server is running (see README for more info)")
        sys.exit()

    warnings.filterwarnings("ignore")    

    # Test bookshop agent with some random queries
    bookshop_agent = get_bookshop_agent()
    session_service = InMemorySessionService()
    bookshop_runner = Runner(
        agent=bookshop_agent,
        app_name="agents",
        session_service=session_service,
        plugins=[
            BookshopAgentPlugin()
        ]
    )

    await bookshop_runner.run_debug(
        "I want biographies written by Stanley"
    )
    
    await bookshop_runner.run_debug(
        "I hate fiction. Do you have anything to recommend? Please no books by Kubick"
    )
    
    await bookshop_runner.run_debug(
        "I'm searching for a biography about a man that runs a company. Can you find anything for me?"
    )
    await bookshop_runner.run_debug(
        "I'm searching for a history book but please nothing about politics."
    )

    # This query should produce nothing
    await bookshop_runner.run_debug(
        "I'm searching for books written by Marinkiewicz"
    )

    # This query should produce nothing
    await bookshop_runner.run_debug(
        "I'm searching for biographies written by Marinkiewicz not related to politics"
    )

    #await bookshop_runner.run_debug(
    #    input("Write your own query! ")
    #)


if __name__=="__main__":
    asyncio.run(main())