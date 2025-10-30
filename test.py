from openai import OpenAI
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# Ollama API 設定（遠端）
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://140.134.60.218:11425/v1')
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY', 'ollama')

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key=OLLAMA_API_KEY, # required, but unused
)

message=input("Enter your message: ")
# response = client.chat.completions.create(
#     model="gemma3:1b",  #"gpt-oss:20b-cloud",
#     messages=[
#         {"role": "user", "content": message}
#     ]
# )
# print(f"User: {message}")
# print(f"AI: {response.choices[0].message.content}")

response = client.chat.completions.create(
    model="gemma3n:e4b",  #"gpt-oss:20b-cloud",
    messages=[
        {"role": "user", "content": message}
    ],
    stream=True
)
print(f"User: {message}")
print("AI: ", end="", flush=True)
for chunk in response:
    content = chunk.choices[0].delta.content or ""
    print(content, end="", flush=True)
print()