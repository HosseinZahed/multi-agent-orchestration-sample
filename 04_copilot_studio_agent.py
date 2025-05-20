
import os
from typing import List
import chainlit as cl
import logging
from copilot_studio_addons.copilot_studio_agent import CopilotAgent
from copilot_studio_addons.directline_client import DirectLineClient
from copilot_studio_addons.copilot_studio_agent_thread import CopilotAgentThread
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService


logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logging.getLogger("copilot_studio_agent").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

client = DirectLineClient(
    copilot_agent_secret=os.getenv("BOT_SECRET"),
    directline_endpoint="https://europe.directline.botframework.com/v3/directline"
)

agent = CopilotAgent(
    id="copilot_studio",
    name="copilot_studio",
    description="copilot_studio",
    directline_client=client,
)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent_service", AgentsService())
    cl.user_session.set("chat_history", ChatHistory())
    thread = CopilotAgentThread(
        directline_client=client,
    )
    cl.user_session.set("thread", thread)


@cl.on_message
async def on_message(user_message: cl.Message):
    thread: CopilotAgentThread = cl.user_session.get("thread")
    agent_service: AgentsService = cl.user_session.get("agent_service")
    chat_history: ChatHistory = cl.user_session.get("chat_history")

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    response = await agent.get_response(messages=user_message.content, thread=thread)

    cl.user_session.set("thread", thread)

    chat_history.add_assistant_message(answer.content)

    # Send the final message
    await cl.Message(content=response.message.content, author=agent.name).send()


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="Copenhagen Weather",
            message="What's the weather like in Copenhagen today?",
        ),
        cl.Starter(
            label="Euroision 2025 Winner",
            message="Who won the Eurovision Song Contest 2025?",
        )
    ]
