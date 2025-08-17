


import os
os.environ["LIVEKIT_API_KEY"] = "APIjqSP6tGk2tFD"
os.environ["LIVEKIT_API_SECRET"] = "HUPwC1ijdSVXImU5dGjxxOoyhjufssPUNMX6VSelp9s"
os.environ["LIVEKIT_URL"] = "https://chat-server.alshifa.me"


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
from livekit import api
from livekit.api.access_token import VideoGrants



async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
    )
    # session = AgentSession(
    #     vad=silero.VAD.load(),
    #     stt=openai.STT(model="whisper-1", api_key=os.environ["OPENAI_API_KEY"]),
    #     llm=openai.LLM(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"]),
    #     tts=openai.TTS(api_key=os.environ["OPENAI_API_KEY"]),
    # )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT.with_ollama(url="http://my-whisper-service.whisper.svc.yarai.local:9000/api/v1"),
        llm=openai.LLM.with_ollama(url="http://ollama.ollama.svc.yarai.local:11434"),
        tts=openai.TTS.with_ollama(url="http://172.16.20.10:8080/v1"),
    )

    token = api.AccessToken(
        os.environ["LIVEKIT_API_KEY"],
        os.environ["LIVEKIT_API_SECRET"]
    ).with_identity("voice-agent") \
     .with_name("Voice Agent") \
     .to_jwt()

    await session.start(
        agent=agent,
        room="default-room",
    )

    await session.generate_reply(instructions="سلام! من دستیار صوتی هستم. می‌تونم کمکت کنم؟")



if __name__ == "__main__":
    cli.run_app(WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.environ["LIVEKIT_API_KEY"],
            api_secret=os.environ["LIVEKIT_API_SECRET"],
            ws_url=os.environ["LIVEKIT_URL"],
        ))