from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MemoryStoreDefaultDefinition,
    MemoryStoreDefaultOptions,
)
import os,time
from dotenv import load_dotenv

load_dotenv()
# Create project client to call Foundry API
project = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
    
)
openai = project.get_openai_client()


# Create a memory store
options = MemoryStoreDefaultOptions(
    chat_summary_enabled=True,
    user_profile_enabled=True,
)
definition = MemoryStoreDefaultDefinition(
    chat_model="gpt-4o",
    embedding_model="text-embedding-3-small",
    options=options,
)
memory_store = project.beta.memory_stores.create(
    name="my_memory_store",
    definition=definition,
    description="Memory store for my agent",
)
print(f"Memory store: {memory_store.name}")
