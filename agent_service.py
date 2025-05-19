import os
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from utils import load_prompt


class AgentsService:
    """Service to manage agents using Azure OpenAI API."""

    def __init__(self):

        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")        
        if not endpoint or not api_key:
            raise EnvironmentError(
                "Missing Azure OpenAI API endpoint, key or deployment.")
        self.base_kernel = Kernel()

    def create_agent(self,
                     agent_name: str,
                     model_name: str,
                     instructions: str = None):
        """Create a simple chat completion agent."""
        # kernel = self.base_kernel.clone()
        agent = ChatCompletionAgent(
            service=AzureChatCompletion(deployment_name=model_name),
            name=agent_name,
            instructions=instructions or load_prompt(agent_name=agent_name),
        )
        return agent

    @staticmethod
    def request_settings() -> OpenAIChatPromptExecutionSettings:
        """Create request settings for the OpenAI service."""
        return OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(
                filters={"excluded_plugins": ["ChatBot"]}
            )
        )
