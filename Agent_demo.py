from agents import Agent, Runner, function_tool


@function_tool  
async def current_time() -> str:
    """Fetch the current time for a given location.

    Args:
        location: The location to fetch the current time for.
    """
    import datetime
    return str(datetime.datetime.now().isoformat())

agent = Agent(
    name="introduction agent",
    instructions="You provide general information and answer questions about various topics.",
    model="gpt-5-mini",
    tools=[current_time],
)


async def main():
    result = await Runner.run(agent, "What time is it?")
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())