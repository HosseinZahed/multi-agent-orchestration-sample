from typing import List
import chainlit as cl
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService

import logging

logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent_service", AgentsService())
    cl.user_session.set("chat_history", ChatHistory())


@cl.on_message
async def on_message(user_message: cl.Message):
    agent_service: AgentsService = cl.user_session.get("agent_service")
    agent: ChatCompletionAgent = agent_service.create_agent(
        agent_name="simple-agent",
        model_name="gpt-4.1-mini",
        instructions="You are a helpful assistant."
    )
    
    chat_history: ChatHistory = cl.user_session.get("chat_history")

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    # Stream the agent's response token by token
    async for token in agent.invoke_stream(
            messages=chat_history
    ):
        if token.content:
            await answer.stream_token(token.content.content)

    chat_history.add_assistant_message(answer.content)

    # Send the final message
    await answer.send()


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="AI Assistant",
            message="Design an AI assistant with frontend, backend, and database integration.",
        ),
        cl.Starter(
            label="Data Analysis Bot",
            message="Create a bot to analyze and visualize data trends.",
        ),
        cl.Starter(
            label="Weather Bot",
            message="How is the weather today?",
        ),
    ]