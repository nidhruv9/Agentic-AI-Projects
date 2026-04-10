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
conversation = openai.conversations.create(
    items=[
        {
            "type": "message",
            "role": "user",
            "content": "What is the largest city in France?",
        }
    ],
)
print(f"Conversation ID: {conversation.id}")

# Add a follow-up message to an existing conversation
openai.conversations.items.create(
    conversation_id=conversation.id,
    items=[
        {
            "type": "message",
            "role": "user",
            "content": "What about Germany?",
        }
    ],
)




# Use a conversation when you want:

# Multi-turn continuity: Keep a stable history across turns without rebuilding context yourself.
# Cross-session continuity: Reuse the same conversation for a user who returns later.
# Easier debugging: Inspect what happened over time (for example, tool calls and outputs).
# When a conversation is used to generate a response (with or without an agent), 
# the full conversation is provided as input to the model. The generated response is then appended to the same conversation.