import asyncio
import os
import datetime
import requests
from dotenv import load_dotenv
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import groq, silero, deepgram , noise_cancellation
from knowledge_tool import search_knowledge_base


load_dotenv()

# ── TOOL 1: Get current time in Pakistan ──────────────────────────────────────
# @function_tool tells LiveKit this is a tool the LLM can call
# The docstring is what the LLM reads to understand WHEN to use this tool
@function_tool
async def get_current_time() -> str:
    """Get the current time and date in Pakistan."""
    pk_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    return f"Current time in Pakistan is {pk_time.strftime('%I:%M %p, %A %d %B %Y')}"


# ── TOOL 2: Get weather for any city ─────────────────────────────────────────
# The parameter 'city' is what the LLM will extract from the conversation
# e.g. user says "weather in Lahore" → LLM calls get_weather(city="Lahore")
# i changed to openweather ai instead of wttr
@function_tool
async def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    try:
        api_key = os.getenv("WEATHER_API_KEY")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Weather in {city}: {desc}, {temp}°C"
    except Exception as e:
        return f"Could not fetch weather for {city}."




@function_tool
async def get_prayer_times(city: str) -> str:
    """Get today's Islamic prayer times for a given city in Pakistan."""
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=PK&method=1"
        response = requests.get(url, timeout=5)
        data = response.json()

        timings = data["data"]["timings"]

        return (
            f"Prayer times in {city}: "
            f"Fajr {timings['Fajr']}, "
            f"Dhuhr {timings['Dhuhr']}, "
            f"Asr {timings['Asr']}, "
            f"Maghrib {timings['Maghrib']}, "
            f"Isha {timings['Isha']}"
        )
    except Exception as e:
        return f"Could not fetch prayer times for {city}."

# ── TOOL 3: Save note via MCP 
@function_tool
async def save_note(text: str) -> str:
    """Save a note by the user to the local notes file via MCP server."""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="cmd",
            args=["/c", "python", "notes_mcp_server.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "save_note",
                    arguments={"text": text}
                )
                return result.content[0].text

    except Exception as e:
        return f"Could not save note: {str(e)}"


# ── TOOL 4: Read notes via MCP 
@function_tool
async def read_notes() -> str:
    """Read all saved notes via MCP server."""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="cmd",
            args=["/c", "python", "notes_mcp_server.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "read_notes",
                    arguments={}
                )
                return result.content[0].text

    except Exception as e:
        return f"Could not read notes: {str(e)}"


# ── AGENT CLASS ───────────────────────────────────────────────────────────────
# tools=[...] passes the three tools to the agent
# Now the LLM knows about these tools and will call them when needed
class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are a helpful voice assistant. 
                Always reply in clear, natural English.
                Keep responses short and conversational — this is a voice chat.
                You have access to tools for weather, time, and math — use them when relevant.""",
             tools=[get_weather, get_prayer_times , get_current_time , save_note , read_notes , search_knowledge_base]
        )


async def entrypoint(ctx):
    print("🔌 [DEBUG] Agent entrypoint started...")
    await ctx.connect()
    print(f"✅ [DEBUG] Connected to room: {ctx.room.name}")

    # drive_toolset = mcp.MCPToolset(
    #     server_params=StdioServerParameters(
    #         command="python",
    #         args=["drive_mcp_server.py"]
    #     )
    # )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=groq.STT(language="en"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=deepgram.TTS(model="aura-asteria-en"),
        # mcp_servers=[
        #     mcp.MCPServerStdio(
        #         command="python",
        #         args=["notes_mcp.py"],
        #     ),]
    )

    print("✅ AgentSession created")

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
    ),
)

    print("🎤 Agent started successfully!")

    await session.generate_reply(
        instructions="Say exactly this: Hello! I am your voice assistant. How can I help you today?"
    )

if __name__ == "__main__":
    print("🚀 Starting LiveKit Agent Worker...")
    from livekit.agents import cli, WorkerOptions
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))



