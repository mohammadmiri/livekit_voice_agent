


import os
os.environ["LIVEKIT_API_KEY"] = "APIjqSP6tGk2tFD"
os.environ["LIVEKIT_API_SECRET"] = "HUPwC1ijdSVXImU5dGjxxOoyhjufssPUNMX6VSelp9s"
os.environ["LIVEKIT_URL"] = "https://chat-server.alshifa.me"
os.environ["DEEPGRAM_API_KEY"] = "911edf98105b5e6c6a037c3131679f42ab8aad19"


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import openai, silero

@function_tool
async def lookup_weather(
    context: RunContext,
    location: str,
):
    """Used to look up weather information."""

    return {"weather": "sunny", "temperature": 70}


username = "your_username"
password = "your_password"
base_url = "https://your-api-endpoint.com"

# Combine into a single URL with auth
auth_url = f"https://{username}:{password}@{base_url}"

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
        tools=[lookup_weather],
    )
    # session = AgentSession(
    #     vad=silero.VAD.load(),
    #     stt=openai.STT(model="whisper-1"),
    #     llm=openai.LLM(model="gpt-4o-mini"),
    #     tts=openai.TTS(),
    # )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT.with_ollama(url="http://my-whisper-service.whisper.svc.yarai.local:9000/api/v1"),
        llm=openai.LLM.with_ollama(url="http://ollama.ollama.svc.yarai.local:11434"),
        tts=openai.TTS.with_ollama(url="http://172.16.20.10:8080/v1"),
    )

    logger.info("Starting agent session...")
    await session.start(agent=agent, room=ctx.room)

    logger.info("Generating initial reply...")
    await session.generate_reply(instructions="از کاربر بپرس  که میتونم کمکت کنم یا نه")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.environ["LIVEKIT_API_KEY"],
            api_secret=os.environ["LIVEKIT_API_SECRET"],
            ws_url=os.environ["LIVEKIT_URL"],
        ))