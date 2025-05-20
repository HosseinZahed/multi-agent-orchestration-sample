from typing import List
import dotenv
import chainlit as cl
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService
import logging

dotenv.load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

agent_service = AgentsService()

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", ChatHistory())
    cl.user_session.set("thread", None)
    agent = await agent_service.get_ai_foundry_agent(
        agent_id="asst_XZCAqENim0oqybvlztbnRz5R"
    )
    cl.user_session.set("agent", agent)

@cl.on_message
async def on_message(user_message: cl.Message):
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    thread: AzureAIAgentThread = cl.user_session.get("thread")
    agent: AzureAIAgent = cl.user_session.get("agent")

    chat_history.add_user_message(user_message.content)       

    response = await agent.get_response(
        messages=chat_history,
        thread=thread
    )

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
            label="Health Insurance Benefits",
            message="What kind of health insurance benefits do I get from Contoso?",
        ),
        cl.Starter(
            label="Euroision 2025 Winner",
            message="Who won the Eurovision Song Contest 2025?",
        )
    ]
