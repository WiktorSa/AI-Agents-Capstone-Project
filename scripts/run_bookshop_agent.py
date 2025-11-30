from google.adk.runners import Runner
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.genai import types

from booskshop_agent.bookshop_agent import get_bookshop_agent, BookshopAgentPlugin

import os
import sys
import asyncio
import warnings
from dotenv import load_dotenv
import requests
from colorama import init, Fore


async def main():
    # Init colorama
    init(autoreset=True)

    # Check if Gemini API key is in .env
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print(
            Fore.RED + f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to .env file"
        )
        sys.exit()

    # Test if the Remote DB Agent server is running before doing any operations
    try:
        response = requests.get(
            f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}", 
            timeout=5
        )

        if response.status_code != 200:
            print(Fore.RED + f"❌ Failed to fetch agent card: {response.status_code}")
            print(Fore.YELLOW + "Make sure the Remote DB Agent server is running (see README for more info)")
            sys.exit()

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"❌ Error fetching agent card: {e}")
        print(Fore.YELLOW + "Make sure the Remote DB Agent server is running (see README for more info)")
        sys.exit()

    warnings.filterwarnings("ignore")    

    bookshop_agent = get_bookshop_agent()
    session_service = DatabaseSessionService(db_url="sqlite:///./db/bookshop_session.db")
    booskshop_runner = Runner(
        agent=bookshop_agent,
        app_name="agents",
        session_service=session_service,
        plugins=[
            BookshopAgentPlugin(log_console=False)
        ]
    )

    try:
        session = await session_service.create_session(
            app_name="agents", user_id="default", session_id="default"
        )
    except:
        session = await session_service.get_session(
            app_name="agents", user_id="default", session_id="default"
        )

    print(Fore.GREEN + "📚 Welcome to the Bookshop Smart Assistant!")
    print(Fore.GREEN + "How can I help you?\n")
    while True:
        print(Fore.YELLOW + "You: ", end="")
        user_query = input()
        print()

        query = types.Content(
            role="user", 
            parts=[types.Part(text=user_query)]
        )

        async for event in booskshop_runner.run_async(
            user_id="default", 
            session_id=session.id, 
            new_message=query
        ):
            if (event.is_final_response() 
                and event.content 
                and event.author == "recommend_agent"
            ):
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        print(Fore.CYAN + part.text)

        print()

if __name__=="__main__":
    asyncio.run(main())