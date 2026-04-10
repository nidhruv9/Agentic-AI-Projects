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
# Create a web search agent
agent = project.agents.create_version(
    agent_name="web-tool-agent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are a helpful assistant that can search the web.",
        tools=[WebSearchTool()],
    ),
)
print(f"Agent: {agent.name}, Version: {agent.version}")

# Generate a response using the agent
response = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
    input="What is the largest city in India?",
    #store= False,
)
print(response.output_text)

# Ask a follow-up question using the previous response
follow_up = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
    previous_response_id=response.id,
    #input="What happened in the news today?",
    input="What is the population of that city?",
    store=False,
)
print(follow_up.output_text)

# Print each output item, including tool calls
for item in response.output:
    if item.type == "web_search_call":
        print(f"[Tool] Web search: status={item.status}")
    elif item.type == "function_call":
        print(f"[Tool] Function call: {item.name}({item.arguments})")
    elif item.type == "file_search_call":
        print(f"[Tool] File search: status={item.status}")
    elif item.type == "message":
        print(f"[Assistant] {item.content[0].text}")