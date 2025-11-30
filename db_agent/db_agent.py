from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.invocation_context import InvocationContext

import sqlite3
from typing import Optional, Any
import os
from datetime import datetime
import logging
import json
import random

def query_books_db(
        included_authors: Optional[list[str]] = None,
        excluded_authors: Optional[list[str]] = None,
        included_categories: Optional[list[str]] = None,
        excluded_categories: Optional[list[str]] = None,
        included_keywords: Optional[list[str]] = None,
        excluded_keywords: Optional[list[str]] = None,
    ) -> dict:
    """
    Query the BOOKS database using optional author-based filters.

    Args:
        included_authors (list[str] | None):
            A list of author last names to include in the search.  
            If None, the search is performed across all authors in the database.  
            The list should contain up to 10 last names (e.g., ["Stepanek", "Aksyonov", "Smith"]).

        excluded_authors (list[str] | None):
            A list of author last names to exclude from the search.  
            If None, no authors are excluded.  
            The list should contain up to 10 last names (e.g., ["Stepanek", "Aksyonov", "Smith"]).

        included_categories (list[str] | None):
            A list of categories to include in the search.
            If None, the search is performed across all categories in the database.  
            The list should contain up to 10 categories (e.g., ["Biography", "Fiction"])

        excluded_categories (list[str] | None):
            A list of categories to exclude from the search.
            If None, no categories are excluded.  
            The list should contain up to 10 categories (e.g., ["Biography", "Fiction"])

        included_keywords (list[str] | None):
            A list of keywords to include in the search (they will be matched to title and description of the books)
            If None, the search is performed across all keywords in the database.  
            The list should contain up to 10 keywords (e.g., ["company", "nation"])

        excluded_keywords (list[str] | None):
            A list of keywords to exclude from the search (they will be matched to title and description of the books)
            If None, no keywords are excluded.  
            The list should contain up to 10 keywords (e.g., ["company", "nation"])

    Returns:
        dict:
            A result dictionary in one of the following formats:

            Success:
                {
                    "status": "success",
                    "books": LIST_OF_BOOKS
                }

            Error:
                {
                    "status": "error",
                    "error_message": "No books found that match given criteria"
                }
    """

    # Adding filters to the query
    filter_part = ""

    # Included authors
    if included_authors is not None:
        filter_part += "("
        for kw in included_authors:
            filter_part += f"UPPER(AUTHORS) LIKE UPPER('%{kw}%') OR "
        filter_part = filter_part[:-4]
        filter_part = filter_part + ") AND "

    # Excluded authors
    if excluded_authors is not None:
        filter_part += "("
        for kw in excluded_authors:
            filter_part += f"UPPER(AUTHORS) NOT LIKE UPPER('%{kw}%') AND "
        filter_part = filter_part[:-5]
        filter_part = filter_part + ") AND "

    # Included Categories
    if included_categories is not None:
        filter_part += "("
        for kw in included_categories:
            filter_part += f"UPPER(CATEGORY) LIKE UPPER('%{kw}%') OR "
        filter_part = filter_part[:-4]
        filter_part = filter_part + ") AND "

    # Excluded Categories
    if excluded_categories is not None:
        filter_part += "("
        for kw in excluded_categories:
            filter_part += f"UPPER(CATEGORY) NOT LIKE UPPER('%{kw}%') AND "
        filter_part = filter_part[:-5]
        filter_part = filter_part + ") AND "

    # Included Keywords
    # Applies to TITLE AND DESCRIPTION
    if included_keywords is not None:
        filter_part += "("
        for kw in included_keywords:
            filter_part += f"UPPER(TITLE) LIKE UPPER('%{kw}%') OR "
            filter_part += f"UPPER(DESCRIPTION) LIKE UPPER('%{kw}%') OR "
        filter_part = filter_part[:-4]
        filter_part = filter_part + ") AND "

    # Excluded Keywords
    # Applies to TITLE, DESCRIPTION
    if excluded_keywords is not None:
        filter_part += "("
        for kw in excluded_keywords:
            filter_part += f"UPPER(TITLE) NOT LIKE UPPER('%{kw}%') AND "
            filter_part += f"UPPER(DESCRIPTION) NOT LIKE UPPER('%{kw}%') AND "
        filter_part = filter_part[:-5]
        filter_part = filter_part + ") AND "
    
    # Add clause and remove last AND
    if filter_part != "":
        filter_part = "WHERE " + filter_part
        filter_part = filter_part[:-4]

    conn = sqlite3.connect('db/books.db')
    # RANDOM() is added so that random 20 books are chosen when more than 20 books meet the criteria
    query = conn.execute(
        f"""
            SELECT
            *
            FROM BOOKS
            {filter_part}
            ORDER BY RANDOM()
            LIMIT 10;
        """
    )
    colname = [d[0] for d in query.description]
    books = [dict(zip(colname, r)) for r in query.fetchall()]

    if len(books) > 0:
        return {
            "status": "success",
            "books": books
        }
    else:
        return {
            "status": "error",
            "error_message": "No books found that match given criteria"
        }

class DBAgentPlugin(BasePlugin):
    def __init__(self, log_level=logging.INFO, log_console=True) -> None:
        super().__init__(name="db_agent_plugin")
        os.makedirs("logs", exist_ok=True)

        self.logger = logging.getLogger("db_agent_logger")
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            log_file_handler = logging.FileHandler("logs/db_agent_logs.log")
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

        self.user_text = None

    async def before_run_callback(
        self, 
        *, 
        invocation_context: InvocationContext
    ) -> Optional[types.Content]:
        """
        Initialize all databases required for the plugin to run correctly
        """

        os.makedirs("db", exist_ok=True)
        if not os.path.exists("db/db_agent_data.db"):
            self.logger.info("[DBAgentPlugin] Creating database for agent data")
            conn = sqlite3.connect('db/db_agent_data.db')
            conn.execute('''
                CREATE TABLE SUCCESSES
                (
                    ID INTEGER PRIMARY KEY NOT NULL,
                    DATE TEXT NOT NULL,
                    USER_QUERY TEXT NOT NULL,
                    FUNC_ARGUMENTS TEXT NOT NULL
                );
            ''')
            conn.execute('''
                CREATE TABLE FAILURES
                (
                    ID INTEGER PRIMARY KEY NOT NULL,
                    DATE TEXT NOT NULL,
                    USER_QUERY TEXT NOT NULL,
                    FUNC_ARGUMENTS TEXT NOT NULL
                );
            ''')
            conn.close()

        else:
            self.logger.info("[DBAgentPlugin] Database for agent data exists")


    async def on_user_message_callback(
        self,
        *,
        invocation_context: InvocationContext,
        user_message: types.Content,
    ) -> Optional[types.Content]:
        self.user_text = str(user_message.parts[0].text).replace("'", "")

    async def after_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
        result: dict,
    ) -> Optional[dict]:
        if tool.name == "query_books_db":
            if result['status'] == "success":
                self.logger.info("[DBAgentPlugin] Query successful")

                if random.random() < 0.1:
                    self.logger.info("[DBAgentPlugin] Saving data from successful query for futher analysis")
                    date = str(datetime.now())
                    func_arguments = json.dumps(tool_args)

                    conn = sqlite3.connect('db/db_agent_data.db')
                    conn.execute(f"INSERT INTO SUCCESSES (DATE,USER_QUERY,FUNC_ARGUMENTS) VALUES ('{date}', '{self.user_text}', '{func_arguments}')")
                    conn.commit()
                    conn.close()
            else:
                self.logger.warning("[DBAgentPlugin] Query failed. Saving data for futher analysis")

                date = str(datetime.now())
                func_arguments = json.dumps(tool_args)

                conn = sqlite3.connect('db/db_agent_data.db')
                conn.execute(f"INSERT INTO FAILURES (DATE,USER_QUERY,FUNC_ARGUMENTS) VALUES ('{date}', '{self.user_text}', '{func_arguments}')")
                conn.commit()
                conn.close()
    
def get_db_agent():
    db_agent = Agent(
        name="db_agent",
        model=Gemini(
            model="gemini-2.5-flash-lite", 
            retry_options=types.HttpRetryOptions(
                attempts=5, 
                exp_base=7,  
                initial_delay=1,
                http_status_codes=[429, 500, 503, 504]
            )
        ),
        description="Agent that queries the BOOKS database for titles matching the user's request.",
        instruction="""
        You are the BOOKS database querying agent. The BOOKS table has fields:
            index: integer
            TITLE: string
            AUTHORS: string
            DESCRIPTION: string
            CATEGORY: string
            PUBLISHER: string
            PRICE: real
            PUBLISH_YEAR: integer

        Your job:
        1. Analyze the user request and extract:
            - Authors the user wants
            - Authors the user explicitly excludes
            - Categories the user wants
            - Categories the user explicitly excludes
            - Keywords the user wants (matched against title & description)
            - Keywords the user explicitly excludes (matched against title & description)
        Only extract information you are very confident about.

        2. Call `query_books_db` with:
            included_authors
            excluded_authors
            included_categories
            excluded_categories
            included_keywords
            excluded_keywords
        Use None for any argument you are uncertain about.

        3. Check the returned `status` field:
            - If success → return the list of books immediately in a specified format
            Book number: <number starting from 1>
            Title: <title>
            Authors: <authors>
            Category: <category>
            Summary: <30-word summary of description>
            Publisher: <publisher>
            Price: <price>
            Publication Year: <year>

            - If error → retry with slightly relaxed arguments.
            - Retry up to 3 times total.

        4. If all retries fail, return the final error message.

        Guidelines:
        - Be generous when interpreting categories (e.g., “autobiography about Obama”
        → included_categories = ["autobiography", "biography", "political memoir"]).
        - If an author is explicitly mentioned, treat it as a strong positive signal.
        - Always return the books in a clean, structured list.
        - Start the search immediately after receiving a request. Do not ask the user questions or request clarification.
        - If no books are found after a query, say that the search returned no results.
        """,
        tools=[query_books_db],
    )

    return db_agent
