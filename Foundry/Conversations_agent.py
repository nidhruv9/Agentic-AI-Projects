import os,time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool
from dotenv import load_dotenv

load_dotenv()
# Format: "https://resource_name.services.ai.azure.com/api/projects/project_name"

# Create project client to call Foundry API
project = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
    
)
openai = project.get_openai_client()

# Create a conversation with an initial user message
conversation = openai.conversations.create()

# print(f"Conversation ID: {conversation.id}")


# First turn
response = openai.responses.create(
    conversation=conversation.id,
    extra_body={
        "agent_reference": {
            "name": "web-tool-agent",
            "type": "agent_reference",
        }
    },
    input="What is the largest city in India?",
)
print(response.output_text)

# Follow-up turn in the same conversation
follow_up = openai.responses.create(
    conversation=conversation.id,
    extra_body={
        "agent_reference": {
            "name":"web-tool-agent",
            "type": "agent_reference",
        }
    },
    input="What is the population of that city?",
)
print(follow_up.output_text)