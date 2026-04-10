
import json
import requests
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, Tool, FunctionTool
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam
from dotenv import load_dotenv

load_dotenv()
# Format: "https://resource_name.services.ai.azure.com/api/projects/project_name"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location (str): The location to fetch weather for.
    :return: Weather information as a string of characters.
    :rtype: str
    """
    
   #calling open weather map API for information retrieval
   #fetching latitude and longitude of the specific location respectively
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
    response=requests.get(url)
    get_response=response.json()
    print("get_response =", get_response)
    print("type(get_response) =", type(get_response))
    latitude=get_response[0]['lat']
    longitude = get_response[0]['lon']

    url_final = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}"
    final_response = requests.get(url_final)
    final_response_json = final_response.json()
    weather=final_response_json['weather'][0]['description']
    if not get_response:
        return f"Could not find location: {city}"
    return weather
    

def get_user_info(user_id: int) -> str:
    """Retrieves user information based on user ID.

    :param user_id (int): ID of the user.
    :rtype: int

    :return: User information as a JSON string.
    :rtype: str
    """
    mock_users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"},
        3: {"name": "Charlie", "email": "charlie@example.com"},
    }

    return mock_users.get(user_id, {"error": "User not found."})

# Create project client to call Foundry API
project = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
    
)
openai = project.get_openai_client()

# Define a function tool for the model to use
user_info_tool = FunctionTool(
    name="get_user_info",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "A user id for a user like 1 or 2.",
            },
        },
        "required": ["user_id"],
        "additionalProperties": False,
    },
    description="Get the information about this user ?",
    strict=True,
)
weather_tool = FunctionTool(
    name="get_weather",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "A city name like Dallas or Chicago",
            },
        },
        "required": ["city"],
        "additionalProperties": False,
    },
    description="Get the curent weather for a city.",
    strict=True,
)

tools: list[Tool] = [user_info_tool, weather_tool]


# Create a prompt agent
agent = project.agents.create_version(
    agent_name="Myagent-weather-user",
    definition=PromptAgentDefinition(
        model=os.getenv("model"),
        instructions=(
            "You are a helpful assistant that can use function tools."
            "use get_weather for weather questions."
            "Use get_user_info for getting the user information."
        ),
        tools=tools,
    ),
)


# Prompt the model with tools defined
response = openai.responses.create(
    #input="What is my horoscope? I am an Aquarius.",
    input="what is the weather in Moscow today ? ",
    #input= "what is the information for user id 2 ?",
    #input = "Which is the biggest state in India ? ",
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)



input_list: ResponseInputParam = []

# Process function calls
for item in response.output:
    if item.type == "function_call":
        if item.name == "get_user_info":
            # Execute the function logic for get_horoscope
            info = get_user_info(**json.loads(item.arguments))

            # Provide function call results to the model
            input_list.append(
                FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps({"user_info": info}),
                )
            )
        elif item.name == "get_weather":
            weather_result = get_weather(**json.loads(item.arguments))
            input_list.append(
                FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps({"weather": weather_result}),
                )
            )

# Submit function results and get the final response
if input_list:
    response = openai.responses.create(
        input=input_list,
        previous_response_id=response.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

print(f"Agent response: {response.output_text}")

# Clean up resources
project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
