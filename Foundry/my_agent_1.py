import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from dotenv import load_dotenv

load_dotenv()
# Format: "https://resource_name.services.ai.azure.com/api/projects/project_name"

# Create project client to call Foundry API
project = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
    
)

# Create a prompt agent
agent = project.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are a helpful assistant.",
    ),
)
print(f"Agent: {agent.name}, Version: {agent.version}")
