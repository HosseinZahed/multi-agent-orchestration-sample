from typing import List
import dotenv
import chainlit as cl
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService
import logging
import os

# Import Azure AI Search client (assume azure-search-documents is installed)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
dotenv.load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("azure.search").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# Azure AI Search configuration (set these in your .env file)
search_client = SearchClient(
    endpoint=os.getenv("AI_SEARCH_ENDPOINT"),
    index_name=os.getenv("AI_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AI_SEARCH_KEY"))
)

agent_service = AgentsService()
agent: ChatCompletionAgent = agent_service.create_default_agent(
    agent_name="rag-agent",
    model_name="gpt-4.1-mini",
    instructions="You are a helpful assistant. Use the provided search results to answer user questions."
)


def retrieve_documents(query: str, top_k: int = 5) -> List[dict]:
    """Retrieve top_k relevant documents from Azure AI Search, including chunk and title."""
    results = search_client.search(query, top=top_k)    
    docs = []
    for result in results:
        doc = {
            "title": result.get("title", "(No Title)"),
            "chunk": result.get("chunk", str(result))
        }
        docs.append(doc)
    return docs


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", ChatHistory())
    cl.user_session.set("thread", None)


@cl.on_message
async def on_message(user_message: cl.Message):
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    thread: ChatHistoryAgentThread = cl.user_session.get("thread")

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    # Inform user that the agent is calling Azure AI Search
    await cl.Message(content="🔎 Agent is calling Azure AI Search to retrieve relevant documents...").send()

    # Retrieve relevant documents from AI Search
    retrieved_docs = retrieve_documents(user_message.content)
    context = "\n\n".join([
        f"Title: {doc['title']}\nContent: {doc['chunk']}" for doc in retrieved_docs
    ])

    # Add context to the chat history for the agent
    chat_history.add_user_message(
        f"[CONTEXT]\n{context}\n[QUESTION]\n{user_message.content}")

    # Stream the agent's response token by token
    async for token in agent.invoke_stream(
            messages=chat_history,
            thread=thread
    ):
        if token.content:
            await answer.stream_token(token.content.content)

    # Add citations (unique titles) at the end of the response
    if retrieved_docs:
        unique_titles = list(dict.fromkeys(doc['title'] for doc in retrieved_docs))
        citations = "\n\nCitations:\n" + "\n".join(f"📄 {title}" for title in unique_titles)
        answer.content += citations

    chat_history.add_assistant_message(answer.content)
    cl.user_session.set("thread", thread)
    await answer.send()


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [

        cl.Starter(
            label="Health Insurance Benefits",
            message="What kind of health insurance benefits do I get?",
        ),
        cl.Starter(
            label="Paternity Leave Policy",
            message="What is the paternity leave policy?",
        ),
    ]
