
import dotenv
from typing import List
import chainlit as cl
from copilot_studio_addons.copilot_studio_agent_thread import CopilotAgentThread
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
client, agent = agent_service.create_copilot_studio_agent(
    agent_name="copilot-studio-agent"
)


@cl.on_chat_start
async def on_chat_start():    
    cl.user_session.set("thread", CopilotAgentThread(directline_client=client))
    cl.user_session.set("chat_history", ChatHistory())


@cl.on_message
async def on_message(user_message: cl.Message):
    thread: CopilotAgentThread = cl.user_session.get("thread")
    chat_history: ChatHistory = cl.user_session.get("chat_history")

    chat_history.add_user_message(user_message.content)    
    
    response = await agent.get_response(messages=user_message.content, thread=thread)

    cl.user_session.set("thread", thread)
    chat_history.add_assistant_message(response.message.content)
    await cl.Message(content=response.message.content).send()


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
