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

billing_agent = ChatCompletionAgent(
    service=AzureChatCompletion(deployment_name=deployment_name),
    name="BillingAgent",
    instructions=(
        "You specialize in handling customer questions related to billing issues. "
        "This includes clarifying invoice charges, payment methods, billing cycles, "
        "explaining fees, addressing discrepancies in billed amounts, updating payment details, "
        "assisting with subscription changes, and resolving payment failures. "
        "Your goal is to clearly communicate and resolve issues specifically about payments and charges."
    ),
)

refund_agent = ChatCompletionAgent(
    service=AzureChatCompletion(deployment_name=deployment_name),
    name="RefundAgent",
    instructions=(
        "You specialize in addressing customer inquiries regarding refunds. "
        "This includes evaluating eligibility for refunds, explaining refund policies, "
        "processing refund requests, providing status updates on refunds, handling complaints related to refunds, "
        "and guiding customers through the refund claim process. "
        "Your goal is to assist users clearly and empathetically to successfully resolve their refund-related concerns."
    ),
)

triage_agent = ChatCompletionAgent(
    service=AzureChatCompletion(deployment_name=deployment_name),
    kernel=kernel,
    name="TriageAgent",
    instructions=(
        "Your role is to evaluate the user's request and forward it to the appropriate agent based on the nature of "
        "the query. Forward requests about charges, billing cycles, payment methods, fees, or payment issues to the "
        "BillingAgent. Forward requests concerning refunds, refund eligibility, refund policies, or the status of "
        "refunds to the RefundAgent. Your goal is accurate identification of the appropriate specialist to ensure the "
        "user receives targeted assistance."
    ),
    plugins=[billing_agent, refund_agent],
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
            label="Sample Request",
            message="""
            I was charged twice for my subscription last month, 
            can I get one of those payments refunded?
            """
        )
    ]
