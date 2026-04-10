import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAISearchTool,
    PromptAgentDefinition,
    AzureAISearchToolResource,
    AISearchIndexResource,
    AzureAISearchQueryType,
)
from dotenv import load_dotenv


load_dotenv()
# Format: "https://resource_name.ai.azure.com/api/projects/project_name"
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
SEARCH_CONNECTION_NAME = os.getenv("SEARCH_CONNECTION_NAME")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")
model=os.getenv("model")

print(SEARCH_CONNECTION_NAME)
print(SEARCH_INDEX_NAME)

# Create clients to call Foundry API
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai = project.get_openai_client()

# Resolve the connection ID from the connection name
azs_connection = project.connections.get(SEARCH_CONNECTION_NAME)
connection_id = azs_connection.id

print(connection_id)

# Create an agent with the Azure AI Search tool
agent = project.agents.create_version(
    agent_name="MyAgent",
    definition=PromptAgentDefinition(
        model=model,
        instructions="""You are a helpful assistant. You must always provide citations for
        answers using the tool and render them as: `[message_idx:search_idx†source]`.""",
        tools=[
            AzureAISearchTool(
                azure_ai_search=AzureAISearchToolResource(
                    indexes=[
                        AISearchIndexResource(
                            project_connection_id=connection_id,
                            index_name=SEARCH_INDEX_NAME,
                            query_type=AzureAISearchQueryType.SIMPLE,
                        ),
                    ]
                )
            )
        ],
    ),
    description="You are a helpful agent.",
)


print(f"Agent created (id: {agent.id},name: {agent.name}, version: {agent.version}")

#Instead of thread we use conversation id and response
conversation= openai.conversations.create()
print(f"Conversation created: {conversation.id}")

response = openai.responses.create(
    conversation=conversation.id,
    input="What are the hotels offered by Margie's Travel in Las Vegas?",
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
)

print("\nAssistant response:\n")
print(response.output_text)

# Clean up agent version when done
project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("\nDeleted agent version")


