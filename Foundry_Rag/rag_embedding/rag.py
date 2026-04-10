import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

deployment_name = os.getenv("get_embed_model")
endpoint = os.getenv("get_oai_base")
api_key = os.getenv("get_oai_key")

print("deployment_name:", deployment_name)
print("endpoint:", endpoint)
print("api_key loaded:", api_key is not None)

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

data = "a lot of festivals are coming"

response = client.embeddings.create(
    model=deployment_name,
    input=data
)

print(response.model_dump_json(indent=2))
