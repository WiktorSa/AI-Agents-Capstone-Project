from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from booskshop_agent.bookshop_agent import get_bookshop_agent, BookshopAgentPlugin

import os
import sys
import asyncio
import warnings
from dotenv import load_dotenv

async def main():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print(
            f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to .env file"
        )
        sys.exit()

    warnings.filterwarnings("ignore")

    booskshop_agent = get_bookshop_agent()
    session_service = InMemorySessionService()
    booskshop_runner = Runner(
        agent=booskshop_agent,
        app_name="agents",
        session_service=session_service,
        plugins=[
            BookshopAgentPlugin()
        ]
    )

    await booskshop_runner.run_debug(
        "I want biographies written by Stanley"
    )
    
    await booskshop_runner.run_debug(
        "I hate fiction. Do you have anything to recommend? Please no books by Kubick"
    )
    
    await booskshop_runner.run_debug(
        "I'm searching for a biography about a man that runs a company. Can you find anything for me?"
    )
    await booskshop_runner.run_debug(
        "I'm searching for a history book but please nothing about politics."
    )

    # This query should produce nothing
    await booskshop_runner.run_debug(
        "I'm searching for books written by Marinkiewicz"
    )
    # This query should produce nothing
    await booskshop_runner.run_debug(
        "I'm searching for biographies written by Marinkiewicz not related to politics"
    )

    #await booskshop_runner.run_debug(
    #    input("Write your own query! ")
    #)


if __name__=="__main__":
    asyncio.run(main())