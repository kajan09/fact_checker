from FAXXCHEXX.llmhandler import LLMHandler
from FAXXCHEXX.utils.llm_client import LocalLLMClient


# Define the LLM client
client  = LocalLLMClient("http://my-llm-server:8000/v1/chat/completions")
handler = LLMHandler(llm_client=client)

# How to use FAXXCHEXX 
result = handler("json Output of FAXXCHEXX for integration in frontend")
