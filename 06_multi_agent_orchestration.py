from typing import List
import dotenv
import chainlit as cl
from semantic_kernel.agents import ChatCompletionAgent, A
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService

import logging

dotenv.load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logging.getLogger("copilot_studio_agent").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent_service", AgentsService())
    cl.user_session.set("chat_history", ChatHistory())
    cl.user_session.set("thread", None)

@cl.on_message
async def on_message(user_message: cl.Message):
    agent_service: AgentsService = cl.user_session.get("agent_service")
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    #thread: Chatompl = cl.user_session.get("thread")
    
    agent: ChatCompletionAgent = agent_service.create_simple_agent(
        agent_name="simple-agent",
        model_name="gpt-4.1-mini",
        instructions="You are a helpful assistant."
    )

    

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
