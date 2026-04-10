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


# Stream a response using the agent
stream = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name":"web-tool-agent",
            "type": "agent_reference",
        }
    },
    input="Explain how agents work in one paragraph.",
    stream=True,
)

for event in stream:
    if hasattr(event, "delta") and event.delta:
        print(event.delta, end="", flush=True)

# For long running operations, you can return results incrementally using 
# streaming or run completely asynchronously using background mode. 
# In these cases, you typically monitor the response until it finishes and 
# then consume the final output items.

# Stream a response
# Streaming returns partial results as they're generated. This approach is 
# useful for showing output to users in real time.