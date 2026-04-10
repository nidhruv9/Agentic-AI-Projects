import json
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, Tool, FunctionTool
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam
from dotenv import load_dotenv

load_dotenv()
# Format: "https://resource_name.services.ai.azure.com/api/projects/project_name"


def get_horoscope(sign: str) -> str:
    """Generate a horoscope for the given astrological sign."""
    return f"{sign}: Next Tuesday you will befriend a baby otter."


# Create project client to call Foundry API
project = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
    
)
openai = project.get_openai_client()

# Define a function tool for the model to use
func_tool = FunctionTool(
    name="get_horoscope",
    parameters={
        "type": "object",
        "properties": {
            "sign": {
                "type": "string",
                "description": "An astrological sign like Taurus or Aquarius",
            },
        },
        "required": ["sign"],
        "additionalProperties": False,
    },
    description="Get today's horoscope for an astrological sign.",
    strict=True,
)

tools: list[Tool] = [func_tool]


# Create a prompt agent
agent = project.agents.create_version(
    agent_name="MyAgent-func",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are a helpful assistant that can use function tools.",
        tools=tools,
    ),
)


# Prompt the model with tools defined
response = openai.responses.create(
    input="What is my horoscope? I am an Aquarius.",
    #input = "Which is the biggest state in India ? ",
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)
print(f"Agent response: {response.output_text}")


input_list: ResponseInputParam = []

# Process function calls
for item in response.output:
    if item.type == "function_call":
        if item.name == "get_horoscope":
            # Execute the function logic for get_horoscope
            horoscope = get_horoscope(**json.loads(item.arguments))

            # Provide function call results to the model
            input_list.append(
                FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps({"horoscope": horoscope}),
                )
            )

# Submit function results and get the final response
response = openai.responses.create(
    input=input_list,
    previous_response_id=response.id,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)

print(f"Agent response: {response.output_text}")

# Clean up resources
project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
