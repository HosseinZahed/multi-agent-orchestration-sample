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
logger = logging.getLogger(__name__)

agent_service = AgentsService()
agent: ChatCompletionAgent = agent_service.create_model_router_agent(
    agent_name="model-router-agent",
    instructions="You are a helpful assistant."
)


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

    # Stream the agent's response token by token
    async for token in agent.invoke_stream(
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
            label="GPT-4.1",
            message="Draft a comprehensive project proposal for an AI-powered healthcare assistant, including objectives, challenges, and ethical considerations."
        ),
        cl.Starter(
            label="GPT-4.1 Mini",
            message="Summarize the latest developments in artificial intelligence in 2024."
        ),
        cl.Starter(
            label="GPT-4.1 Nano",
            message="What is the capital of Denmark?"
        ),

    ]
