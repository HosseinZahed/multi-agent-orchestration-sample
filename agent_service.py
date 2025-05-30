import os
from contextlib import asynccontextmanager
from semantic_kernel import Kernel
from semantic_kernel.kernel import KernelArguments
from semantic_kernel.agents import ChatCompletionAgent, AzureAIAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from azure.identity.aio import DefaultAzureCredential
from copilot_studio_addons.copilot_studio_agent import CopilotAgent
from copilot_studio_addons.directline_client import DirectLineClient
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

    def create_default_agent(self,
                             agent_name: str,
                             model_name: str,
                             instructions: str = None,
                             plugins: list = None):
        """Create a simple chat completion agent."""
        kernel = self.base_kernel.clone()
        kernel.add_service(AzureChatCompletion(deployment_name=model_name))
        agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=instructions or load_prompt(agent_name=agent_name),
            plugins=plugins or [],
            arguments=KernelArguments(
                request_settings=self.request_settings()
            )
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

    async def get_ai_foundry_agent(self, agent_id: str):
        client = await self.get_ai_foundry_client().__aenter__()

        agent_definition = await client.agents.get_agent(
            agent_id=agent_id
        )

        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
        )
        return agent

    def get_copilot_studio_agent(self, agent_name: str):
        """Create a Copilot Studio agent."""
        client = DirectLineClient(
            copilot_agent_secret=os.getenv("BOT_SECRET"),
            directline_endpoint=os.getenv("DIRECTLINE_ENDPOINT"),
        )

        agent = CopilotAgent(
            id=agent_name,
            name=agent_name,
            description="Copilot Studio Agent",
            directline_client=client,
        )
        return client, agent

    def create_model_router_agent(self,
                                  agent_name: str,
                                  model_name: str,
                                  instructions: str = None,
                                  plugins: list = None):
        """Create a model router agent."""
        kernel = self.base_kernel.clone()
        kernel.add_service(AzureChatCompletion(
            deployment_name="model-router",
            api_version="2024-12-01-preview"))
        agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=instructions or load_prompt(agent_name=agent_name),
            plugins=plugins or [],
            arguments=KernelArguments(
                request_settings=self.request_settings()
            )
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
            ),
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
