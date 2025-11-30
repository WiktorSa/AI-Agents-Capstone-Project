# AI-Agents-Capstone-Project-2025

**Capstone Project made as a part of 5-Day AI Agents Intensive Course with Google 2025**   
**Category**: Enterprise Agents  
**Project Name**: Smart Bookshop Assistant

# Problem formulation
Let's imagine a following scenario:  
You are a student searching for some books on the topic of AI Agents. You could of course just type "AI Agents book" in the Google search or in any bookshop search system yet after this you still need to manually check each suggestion and verify whether or not this is what you are looking for. What if you are searching for a certain topic related to AI Agents? The search can become very tedious quickly.

Solution - use AI Agents! AI Agents may use your message to select books that fit your criteria the best. Additionally they can give you a quick summary of each of the suggestions. That way you can quickly find interesting books without having to manually check each suggestion.

In this project we are using [Books Dataset by Elvin Rustamov](https://www.kaggle.com/datasets/elvinrustam/books-dataset) to simulate a virtual bookstore. We will be implementing a simple AI Agents System that will accept user message and return a recommended list of books. If no books are found that meet user criteria the system will communicate that to the user.

NOTE - this project is just a prototype! It's meant to show the strengths of AI Agents - not implement an actually working Bookshop website. We will use console to communicate with the AI Agents.

# System Architecture
![System Architecture](assets/agents_architecture.jpg)

How the system works:
1. The user asks about book recommendations e.g., books about history
2. search_agent accepts the user input. Using session memory it modifies the original user prompt (e.g., user doesn't like politics = the prompt will now include that user does not want history books related to politics). This prompt is passed using A2A protocol to the db_agent.
3. db_agent searches for authors, categories and keywords in the prompt it receives. Than it queries the database for books that meet this criteria. The list of books is passed to the search_agent
4. search_agent passes the list of books with original user prompt to the recommend_agent
5. recommend_agent analyses the list of books and original user prompt and selects books that fit user criteria best. The list is returned to the user as a text

# Features of the AI Agents System
This project utilizes:
- Multi-agent system, including any combination of:
    - Agent powered by an LLM (db_agent, search_agent, recommend_agent)
    - Sequential agents (book_search_agent_system)
- Tools, including:
    - custom tools (function to query database used by db_agent)
- Sessions & Memory
    - Sessions & state management (DatabaseSessionService)
- Observability: Logging (logging the performance of db_agent and book_search_agent_system, saving a part of successful queries and all failed queries to the database for future analysis)
- A2A Protocol (communication between db_agent and search_agent)

# Setup
The project was tested on Ubuntu 24.04.3 LTS and Python 3.12.3. I cannot guarantee that the project will work on other configurations.

## Dataset download
[Download Books Dataset by Elvin Rustamov](https://www.kaggle.com/datasets/elvinrustam/books-dataset) and extract the .zip file  
Create dataset folder at the project level and place BooksDatasetClean.csv in it  

## Environment configuration
Create a .env file with a following configuration

```properties
GOOGLE_API_KEY=<Your Google AI Studio API Key>
```  
[You can generate your own Google AI Studio API Key here](https://aistudio.google.com/)

Create a virtual environment by running these commands in the console

```properties
python3 -m virtualenv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```  

## Creating books database

Before you start experimenting with the AI Agents system you need to create a books database. Run the following commands in the console.

```properties
source venv/bin/activate
python -m scripts.create_books_db
```  

## How proper configuration looks


uvicorn scripts.a2a_db_agent:a2a_app --host localhost --port 8001
http://localhost:8001/.well-known/agent-card.json

## 
Create .env file