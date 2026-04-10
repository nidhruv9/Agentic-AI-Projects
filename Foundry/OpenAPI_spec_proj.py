import os
from dotenv import load_dotenv
import jsonref
from typing import Any, cast
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.ai.projects.models import (
    PromptAgentDefinition,
    OpenApiTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
)


load_dotenv()
# Format: "https://resource_name.services.ai.azure.com/api/projects/project_name"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
# Create project client to call Foundry API
project = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
    
)

weather_asset_file_path = os.path.join(
    os.path.dirname(__file__),
    "openweather_minimal_openapi.json"
)
#print(weather_asset_file_path)
# print(os.path.exists(weather_asset_file_path))
openai = project.get_openai_client()

with open(weather_asset_file_path, "r") as f:
    openapi_weather = cast(dict[str, Any], jsonref.loads(f.read()))

# Initialize agent OpenAPI tool using the read in OpenAPI spec
weather_tool = OpenApiTool(
    openapi=OpenApiFunctionDefinition(
        name="get_weather",
        spec=openapi_weather,
        description="Retrieve weather information for a location.",
        auth=OpenApiAnonymousAuthDetails(),
    )
)


# Create a prompt agent
agent = project.agents.create_version(
    agent_name="my-weather-agent",
    definition=PromptAgentDefinition(
        model=os.getenv("model"),
        instructions=f"""
You are a helpful assistant.

When the user asks for weather:
1. First call get_direct_geocoding.
2. Pass:
- q as the city name
- limit as 1
- appid as {OPENWEATHER_API_KEY}
3. Then read lat and lon from the first result.
4. Call get_current_weather.
5. Pass:
- lat from the first call
- lon from the first call
- units as imperial
- appid as {OPENWEATHER_API_KEY}
6. Summarize the weather clearly.
""",
        tools=[weather_tool],
    ),
)
print(f"Agent: {agent.name}, Version: {agent.version}")

# Ask the agent a question
response = openai.responses.create(
    input="What's the weather in Seattle?",
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
)

print("Agent response")
print(response.output_text)