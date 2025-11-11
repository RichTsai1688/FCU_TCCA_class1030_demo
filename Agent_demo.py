# Json Agent Demo
from agents import Agent, Runner, function_tool, WebSearchTool

import os
os.environ["OPENAI_API_KEY"]=""

@function_tool  
async def current_time() -> str:
    """Fetch the current time for a given location.

    Args:
        location: The location to fetch the current time for.
    """
    import datetime
    return str(datetime.datetime.now().isoformat())

@function_tool
async def my_favor_food(name: str) -> str:
    """回覆使用者該名對象愛吃的東西.

    Args:
        name: The name of the person to greet.
    """
    return f"Hello, {name}! favorite food is pizza."


agent = Agent(
    name="introduction agent",
    instructions="You provide general information and answer questions about various topics.",
    model="gpt-5-mini",
    tools=[current_time, my_favor_food, WebSearchTool()],
)

from openai.types.responses import ResponseTextDeltaEvent
async def main():
    result = Runner.run_streamed(
        agent,
        input="嗨，PETERY 最喜歡吃什麼",
        max_turns=3,
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                tool_name=getattr(event.item.raw_item, "name", type(event.item.raw_item).__name__)
                print(f"[Tool Call] {tool_name}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

# async def main():
#     result = await Runner.run(agent, "請上網查詢精密學程主任是誰?")
#     print(result.final_output)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())