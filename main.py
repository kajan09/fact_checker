from FAXXCHEXX.llmhandler import LLMHandler
from FAXXCHEXX.utils.llm_client import LocalLLMClient


# Define the LLM client
client  = LocalLLMClient("http://my-llm-server:8000/v1/chat/completions")


# How to use FAXXCHEXX 
result = handler("string ")
