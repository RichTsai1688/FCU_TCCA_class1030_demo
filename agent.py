from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
import asyncio
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# Ollama API 設定（本地）
OLLAMA_LOCAL_BASE_URL = os.getenv('OLLAMA_LOCAL_BASE_URL', 'http://localhost:11434/v1')
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY', '')

client = AsyncOpenAI(base_url=OLLAMA_LOCAL_BASE_URL, api_key=OLLAMA_API_KEY)

my_agent = Agent(
    name="Input agent",
    # instructions="Handoff to the appropriate agent based on the language of the request.",
    model=OpenAIChatCompletionsModel(model="gemma3:1b", openai_client=client)
)

async def main():
    result = Runner.run_streamed(
        my_agent,
        input="嗨，你知道法國的首都嗎？",
        max_turns=30,
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())