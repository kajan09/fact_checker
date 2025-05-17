import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama




# ollama
ollama = Ollama(model="nomic-embed-text", request_timeout=1000.0)

# send a prompt directly
response = ollama.complete("Is smoking bad for you?")

print(response)