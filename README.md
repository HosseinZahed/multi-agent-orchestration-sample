# Multi-Agent Orchestration Sample 🤖🤝

Welcome! This project demonstrates how to orchestrate multiple AI agents using Python, Chainlit, and Azure OpenAI. Perfect for prototyping, debugging, and building advanced conversational AI solutions! 🚀

## Getting Started 🏁

### 1. Clone the Repository
```bash
git clone https://github.com/HosseinZahed/multi-agent-orchestration-sample
cd multi-agent-orchestration-sample
```

### 2. Install Requirements 📦
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables ⚙️
- Copy `.env.sample` to `.env`:
  ```bash
  cp .env.sample .env
  ```
- Fill in your Azure OpenAI, Copilot Studio, and other credentials in `.env`:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_AI_AGENT_PROJECT_CONNECTION_STRING`
  - `AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME`
  - For Copilot Studio, get `BOT_SECRET` from Copilot Studio Agent (Settings > Security > Web Channel).
  - `DIRECTLINE_ENDPOINT` for DirectLine API endpoint.

### 4. Run an Example 🏃‍♂️
Pick one of the example scripts and run it with Chainlit:

```bash
chainlit run 01_default_agent.py -w
```

Replace `01_default_agent.py` with any of the following to try different scenarios:
- `01_default_agent.py` – Basic agent chat 🤖
- `02_agent_with_plugin.py` – Agent with date/time plugin 🧩
- `03_ai_foundry_agent.py` – Azure AI Foundry agent integration ☁️
- `04_copilot_studio_agent.py` – Copilot Studio agent integration 🦾
- `05_agent_with_mcp.py` – Agent with GitHub MCP plugin integration 🛠️
- `06_multi_agent_orchestration_implicit.py` – Implicit multi-agent orchestration 🔄
- `07_multi_agent_orchestration_explicit.py` – Explicit multi-agent orchestration with function call tracing 🕹️
- `08_agent_with_rag.py` – Agent with Azure AI Search (RAG) integration 📄
- `09_model_router.py` – Agent with a Model Router that automatically selects the optimal model for each request.

Open the provided local URL in your browser to chat with your agents!

## .env.sample Example 📝
```env
#AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1-mini
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your_api_key>
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING=<your_connection_string>
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=<your_model_deployment_name>

#Copilot Studio Agent
BOT_SECRET="copy from Copilot Studio Agent, under Settings > Security > Web Channel"
DIRECTLINE_ENDPOINT="https://europe.directline.botframework.com/v3/directline"

#Azure Search (for 08_agent_with_rag.py)
AI_SEARCH_ENDPOINT="https://<your-endpoint>.search.windows.net"
AI_SEARCH_KEY="<your_search_key>"
AI_SEARCH_INDEX="<your_index_name>"
```

## Customizing Agent Prompts 📝
- Prompts for agents can be customized by editing or adding `.prompty` files in the `prompts/` directory. Each agent can have its own prompt file named after the agent (e.g., `default-agent.prompty`).

## Utility Modules ⚙️
- `plugin_service.py`: Contains example plugins (e.g., `DateTimePlugin`) for agent tool augmentation.
- `utils.py`: Helper functions for loading prompts and other utilities.

## Useful Links 🔗
- [Chainlit Documentation](https://docs.chainlit.io) 📚
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/) ☁️

---
Happy coding! 💻✨
