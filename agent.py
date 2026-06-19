import asyncio
import os
import datetime
import requests
from dotenv import load_dotenv
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import groq, silero, deepgram , noise_cancellation , google, elevenlabs
from knowledge_tool import search_knowledge_base
import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

#Reading the yaml file

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

llm_config = config["llm"]
stt_config = config["stt"]
tts_config = config["tts"]
agent_config = config["agent"]



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



#Tool for getting the Prayer timings for any specific city
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

# Tool for answering the generic questions
@function_tool
async def general_knowledge(query: str) -> str:
    """This is the FINAL FALLBACK tool. Use this whenever search_knowledge_base 
    returns NOT_RELEVANT, or whenever a question is clearly outside the course 
    slides (general knowledge, sports, celebrities, current events, history, 
    science, etc). NEVER tell the user you don't know or that they should search 
    themselves — always use this tool instead to give them a real answer."""
    try:
        # For now, answer using the LLM's own general knowledge.
        # This just signals to the model: "go ahead and answer normally."
        return f"GENERAL_KNOWLEDGE_MODE: Answer this question directly and confidently using your own knowledge: {query}"
    except Exception as e:
        return f"Could not process general knowledge query: {str(e)}"
    

    # ── TOOL: Send Email via SMTP ─────────────────────────────────────────────────
@function_tool
async def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email to someone. Use this when the user asks to email, send a 
    message, or write to someone via email. You need their email address, a 
    subject, and the message content."""
    try:
        sender_email = os.getenv("GMAIL_ADDRESS")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        return f"Email sent successfully to {to_email}"

    except Exception as e:
        return f"Could not send email: {str(e)}"

# ── AGENT CLASS ───────────────────────────────────────────────────────────────
# tools=[...] passes the three tools to the agent
# Now the LLM knows about these tools and will call them when needed
class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""Tum ek madadgar voice assistant ho.
                Hamesha Roman Urdu mein jawab dou, halki si Pakistani lehja ke saath.
                Jawab chota aur baat-cheet wala rakho — yeh voice chat hai.""" , 
             tools=[get_weather, get_prayer_times , get_current_time , save_note , read_notes , search_knowledge_base , general_knowledge , send_email]
        )


async def entrypoint(ctx):
    print("🔌 [DEBUG] Agent entrypoint started...")
    await ctx.connect()
    print(f"✅ [DEBUG] Connected to room: {ctx.room.name}")

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(
            model=stt_config["model"],
            language=stt_config["language"]
        ),
        llm=groq.LLM(model=llm_config["model"]),
        tts=elevenlabs.TTS(
            model=tts_config["model"],
            voice_id=tts_config["voice_id"]
        ),
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
        instructions=f"Greet the user by saying: {agent_config['greeting']}"
    )

if __name__ == "__main__":
    print("🚀 Starting LiveKit Agent Worker...")
    from livekit.agents import cli, WorkerOptions
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


