from FAXXCHEXX.llmhandler import LLMHandler
from FAXXCHEXX.utils.llm_client import LocalLLMClient

client  = LocalLLMClient("http://my-llm-server:8000/v1/chat/completions")
handler = LLMHandler(llm_client=client)

# Now you can:
result = handler("This is the transcript that came out of Whisper…")
