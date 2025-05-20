from typing import List
import dotenv
import chainlit as cl
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService

import logging

dotenv.load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logging.getLogger("copilot_studio_agent").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

agent_service = AgentsService()

# Create a orchestrator agent
orchestrator_agent: ChatCompletionAgent = agent_service.create_simple_agent(
    agent_name="questioner-agent",
    model_name="gpt-4.1-mini",
    instructions=""" You are a helpful assistant.
    Use the knowledge base to answer the user's questions.
    After answering the question, use the search tool 
    to find more information about the topic. 
    """
)

# Create a Copilot Studio agent
directline_client, search_agent = agent_service.create_copilot_studio_agent(
    agent_name="copilot-studio-agent"
)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent_service", AgentsService())
    cl.user_session.set("chat_history", ChatHistory())
    cl.user_session.set("thread", None)


@cl.on_message
async def on_message(user_message: cl.Message):
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    thread: ChatHistoryAgentThread = cl.user_session.get("thread")

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    async for token in orchestrator_agent.invoke_stream(
            messages=chat_history,
            thread=thread
    ):
        if token.content:
            await answer.stream_token(token.content.content)

    chat_history.add_assistant_message(answer.content)
    cl.user_session.set("thread", thread)
    await answer.send()


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="Today's date and time",
            message="What's the date and time?",
        ),
        cl.Starter(
            label="Health Insurance Benefits",
            message="What kind of health insurance benefits do I get from Contoso?",
        ),
        cl.Starter(
            label="Euroision 2025 Winner",
            message="Who won the Eurovision Song Contest 2025?",
        )
    ]
