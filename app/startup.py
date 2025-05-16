# startup.py  (imported by main)
import whisper, openai

whisper_model = whisper.load_model("small")          # stays in RAM / GPU
openai_client  = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
LLM_MODEL = "meditron:70b"
