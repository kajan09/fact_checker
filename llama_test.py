import openai
import time
import json
import textwrap


# ./bin/ollama start    # run the model in interactive mode# 
# 

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # dummy key, not used by Ollama
)

start_time = time.time()  # start timing
MODEL_NAME = "meditron:7b"

client.chat.completions.create(
    model=MODEL_NAME,
    temperature=0,
    messages=[{"role": "user", "content": "ping"}],
    max_tokens=1
)

SYSTEM_PROMPT = textwrap.dedent("""
    You are Med-Check GPT.
    Task: Evaluate the medical claim provided by the user.
    • Think briefly using current medical consensus.
    • Return a single-line JSON object with keys:
      - "score"     : integer 0-100 (truthfulness)
      - "verdict"   : "Correct", "Partially correct", or "Incorrect"
      - "explanation": ≤ 30 words
    End your answer with the token <END>
""").strip()

claim = "Smoking is very healthy for your health."

response = client.chat.completions.create(
    model=MODEL_NAME,
    temperature=0,        # deterministic
    top_p=0.9,            # optional, keeps rare tokens
    max_tokens=128,
    stop=["<END>"],
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": claim}
    ]
)

end_time = time.time()  # end timing
duration = end_time - start_time

# Print response and timing
print(response.choices[0].message.content)
print(f"\nProcessing time: {duration:.2f} seconds")
