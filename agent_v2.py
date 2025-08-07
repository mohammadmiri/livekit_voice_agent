import os
import logging
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    cli,
    function_tool,
    WorkerOptions,
)
from livekit.plugins import deepgram, elevenlabs, openai, silero

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = "sk-gerdoo-yGpgm4inroXwMQIT4BmtT3BlbkFJ2oidwMoQ3pp1H4yM5tb8"
os.environ["LIVEKIT_API_KEY"] = "APIjqSP6tGk2tFD"
os.environ["LIVEKIT_API_SECRET"] = "HUPwC1ijdSVXImU5dGjxxOoyhjufssPUNMX6VSelp9s"
os.environ["LIVEKIT_URL"] = "wss://chat-server.alshifa.me"
os.environ["DEEPGRAM_API_KEY"] = "911edf98105b5e6c6a037c3131679f42ab8aad19"

@function_tool
async def lookup_weather(context: RunContext, location: str):
    return {"weather": "sunny", "temperature": 70}

async def entrypoint(ctx: JobContext):
    logger.info("Connecting to room...")
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name} as {ctx.identity}")

    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
        tools=[lookup_weather],
    )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(),
    )

    logger.info("Starting session...")
    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions="greet the user and ask about their day")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
