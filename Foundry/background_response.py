import os,time
from time import sleep
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
openai = project.get_openai_client()

# Start a background response using the agent
response = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": "web-tool-agent",
            "type": "agent_reference",
        }
    },
    input="Write a detailed analysis of renewable energy trends.",
    background=True,
)

# Poll until the response completes
while response.status in ("queued", "in_progress"):
    sleep(2)
    response = openai.responses.retrieve(response.id)

print(response.output_text)

# Background mode runs the agent asynchronously, which is useful 
# for long-running tasks such as complex reasoning or image generation. 
# Set background to true and then poll for the response status until it completes.