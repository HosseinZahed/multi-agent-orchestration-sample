from typing import List
import dotenv
import chainlit as cl
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.contents import ChatHistory
from agent_service import AgentsService
from semantic_kernel.connectors.mcp import MCPStdioPlugin
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


@cl.on_message
async def on_message(user_message: cl.Message):
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    thread: ChatHistoryAgentThread = cl.user_session.get("thread")

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    async with MCPStdioPlugin(
        name="Github",
        description="Github Plugin",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
    ) as github_plugin:
        agent: ChatCompletionAgent = agent_service.create_default_agent(
            agent_name="github-agent",
            model_name="gpt-4.1-nano",
            instructions="Answer questions about any github project.",
            plugins=[github_plugin],
        )

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
            label="Top 5 python issues",
            message="What are the latest 5 python issues in Microsoft/semantic-kernel?",
        ),
        cl.Starter(
            label="Issue #10785?",
            message="What is the status of issue #10785 in Microsoft/semantic-kernel?",
        ),
        cl.Starter(
            label="Top 5 contributors",
            message="Who are the top 5 contributors to Microsoft/semantic-kernel?",            
        )
    ]
