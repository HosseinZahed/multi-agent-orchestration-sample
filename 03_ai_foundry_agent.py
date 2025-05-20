from typing import List
import chainlit as cl
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService
import logging


logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent_service", AgentsService())
    cl.user_session.set("chat_history", ChatHistory())


@cl.on_message
async def on_message(user_message: cl.Message):
    agent_service: AgentsService = cl.user_session.get("agent_service")
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    chat_history.add_user_message(user_message.content)
    thread: AzureAIAgentThread = None
    answer = cl.Message(content="")

    async with agent_service.get_ai_foundry_client() as client:

        agent_definition = await client.agents.get_agent(
            agent_id="asst_XZCAqENim0oqybvlztbnRz5R"
        )

        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
        )

        # Stream the agent's response token by token
        response = await agent.get_response(
            messages=chat_history,
            thread=thread
        )
        print(response)
        answer.content = str(response)

        # async for token in agent.invoke_stream(
        #     message=user_message.content,
        #     thread=thread
        # ):
        #     if token.content:
        #         await answer.stream_token(token.content.content)

        chat_history.add_assistant_message(str(response))

        # Send the final message
        await answer.send()


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
