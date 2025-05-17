#!/usr/bin/env python3
import openai
import time


# 1. Initialize client

print("Starting client...\n")
t0 = time.time()

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
t1 = time.time()
print(f"Client initialized.⏱ {t1-t0:.2f} s \n")

# 2. Send one chat request and get the response
print("Calculating response...\n")
t0 = time.time()

response = client.chat.completions.create(
    model="meditron:70b",
    messages=[{"role": "user", "content": "What’s the capital of France?"}],
    temperature=0.1,
)
t1 = time.time()
print(f"Response calculated.⏱ {t1-t0:.2f} s \n")
# 3. Print the model’s answer
print(response.choices[0].message.content.strip())

