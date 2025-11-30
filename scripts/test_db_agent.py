from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from db_agent.db_agent import get_db_agent, DBAgentPlugin

import os
import sys
import asyncio
from dotenv import load_dotenv

async def main():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print(
            f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to .env file"
        )
        sys.exit()

    db_agent = get_db_agent()
    session_service = InMemorySessionService()
    db_runner = Runner(
        agent=db_agent,
        app_name="agents",
        session_service=session_service,
        plugins=[
            DBAgentPlugin()
        ]
    )

    await db_runner.run_debug(
        "I want biographies written by Stanley"
    )
    
    await db_runner.run_debug(
        "I hate fiction. Do you have anything to recommend? Please no books by Kubick"
    )
    
    await db_runner.run_debug(
        "I'm searching for a biography about a man that runs a company. Can you find anything for me?"
    )
    await db_runner.run_debug(
        "I'm searching for a history book but please nothing about politics."
    )

    # This query should produce nothing
    await db_runner.run_debug(
        "I'm searching for books written by Marinkiewicz"
    )
    # This query should produce nothing
    await db_runner.run_debug(
        "I'm searching for biographies written by Marinkiewicz not related to politics"
    )

    #await db_runner.run_debug(
    #    input("Write your own query! ")
    #)


if __name__=="__main__":
    asyncio.run(main())