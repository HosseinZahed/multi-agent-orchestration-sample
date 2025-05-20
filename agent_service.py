import os
from contextlib import asynccontextmanager
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, AzureAIAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from azure.identity.aio import DefaultAzureCredential


from utils import load_prompt
from plugin_service import DateTimePlugin


class AgentsService:
    """Service to manage agents using Azure OpenAI API."""

    def __init__(self):

        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not endpoint or not api_key:
            raise EnvironmentError(
                "Missing Azure OpenAI API endpoint, key or deployment.")
        self.base_kernel = Kernel()

    def create_simple_agent(self,
                            agent_name: str,
                            model_name: str,
                            instructions: str = None):
        """Create a simple chat completion agent."""
        kernel = self.base_kernel.clone()
        kernel.add_service(AzureChatCompletion(deployment_name=model_name))
        agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=instructions or load_prompt(agent_name=agent_name),
        )
        return agent

    def create_agent_with_plugin(self,
                                 agent_name: str,
                                 model_name: str,
                                 instructions: str = None):
        """Create a chat completion agent with a plugin."""
        kernel = self.base_kernel.clone()
        kernel.add_service(AzureChatCompletion(deployment_name=model_name))
        agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            plugins=[DateTimePlugin()],
            instructions=instructions or load_prompt(agent_name=agent_name),
        )
        return agent
    
    @asynccontextmanager
    async def get_ai_foundry_client(self):
        async with DefaultAzureCredential() as creds:
            async with AzureAIAgent.create_client(credential=creds) as client:
                yield client   

    @staticmethod
    def request_settings() -> OpenAIChatPromptExecutionSettings:
        """Create request settings for the OpenAI service."""
        return OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(
                filters={"excluded_plugins": ["ChatBot"]}
            )
        )
