from typing import List
import dotenv
import chainlit as cl
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.filters import FunctionInvocationContext
from semantic_kernel.contents import ChatHistory
import logging

dotenv.load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logging.getLogger("copilot_studio_agent").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# Define the auto function invocation filter that will be used by the kernel


async def function_invocation_filter(context: FunctionInvocationContext, next):
    """A filter that will be called for each function call in the response."""
    if "messages" not in context.arguments:
        await next(context)
        return
    print(
        f"    Agent [{context.function.name}] called with messages: {context.arguments['messages']}")
    await next(context)
    print(
        f"    Response from agent [{context.function.name}]: {context.result.value}")

# Deployment name
deployment_name = "gpt-4.1-mini"

# Create and configure the kernel.
kernel = Kernel()

# The filter is used for demonstration purposes to show the function invocation.
kernel.add_filter("function_invocation", function_invocation_filter)

device_support_agent = ChatCompletionAgent(
    service=AzureChatCompletion(deployment_name=deployment_name),
    name="device_support_agent",
    instructions=(
        "You are an expert in hearing aid device support. "
        "Assist users with troubleshooting device issues, connectivity problems, battery questions, "
        "cleaning and maintenance, and general usage tips for hearing aids. "
        "Your goal is to help users resolve technical or operational issues with their hearing aids."
    ),
)

warranty_repair_agent = ChatCompletionAgent(
    service=AzureChatCompletion(deployment_name=deployment_name),
    name="warranty_repair_agent",
    instructions=(
        "You specialize in warranty and repair inquiries for hearing aids. "
        "Assist users with questions about warranty coverage, repair processes, service timelines, "
        "replacement options, and how to initiate a repair or warranty claim. "
        "Your goal is to guide users through warranty and repair procedures for their hearing aids."
    ),
)

triage_agent = ChatCompletionAgent(
    service=AzureChatCompletion(deployment_name=deployment_name),
    kernel=kernel,
    name="triage_agent",
    instructions=(
        "Your role is to evaluate the user's request and forward it to the appropriate agent based on the nature of "
        "the query. Forward requests about device troubleshooting, connectivity, batteries, or usage to the "
        "DeviceSupportAgent. Forward requests about warranty, repairs, service, or replacement to the WarrantyRepairAgent. "
        "Your goal is accurate identification of the appropriate specialist to ensure the user receives targeted assistance."
    ),
    plugins=[device_support_agent, warranty_repair_agent],
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

    async for token in triage_agent.invoke_stream(
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
            label="Device Issue",
            message="My hearing aid keeps disconnecting from my phone. How can I fix this?"
        ),
        cl.Starter(
            label="Warranty Question",
            message="Is my hearing aid still under warranty, and how do I get it repaired?"
        ),
        cl.Starter(
            label="Cleaning Advice",
            message="What is the best way to clean my hearing aid to keep it working well?"
        )
    ]
