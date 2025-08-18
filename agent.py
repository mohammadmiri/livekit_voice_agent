


import os
os.environ["LIVEKIT_API_KEY"] = "APIjqSP6tGk2tFD"
os.environ["LIVEKIT_API_SECRET"] = "HUPwC1ijdSVXImU5dGjxxOoyhjufssPUNMX6VSelp9s"
os.environ["LIVEKIT_URL"] = "185.149.192.38:7880"
os.environ["OPENAI_API_KEY"] = ""


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
    #     stt=openai.STT(
    #         model="whisper-1",
    #     ),
    #     llm=openai.LLM(model="gpt-4o-mini"),
    #     tts=openai.TTS(
    #         model="tts-1",
    #         voice="ash",
    #         instructions="Speak in a friendly and conversational tone.",
    #     ),
    #     vad=silero.VAD.load(),
    # )

    session = AgentSession(
        vad=silero.VAD.load(),

        stt=openai.STT(
            base_url="http://my-whisper-service.whisper.svc.yarai.local:9000/v1"
        ),

        llm=openai.LLM.with_ollama(
            base_url="http://ollama.ollama.svc.yarai.local:11434",
            model="llama3.1"
        ),

        tts=openai.TTS(
            base_url="http://172.16.20.10:8080/v1"
        ),
    )

    # token = api.AccessToken(
    #     os.environ["LIVEKIT_API_KEY"],
    #     os.environ["LIVEKIT_API_SECRET"]
    # ).with_identity("voice-agent") \
    #  .with_name("Voice Agent") \
    #  .with_grants(
    #     VideoGrants(
    #         room_join=True,
    #         room="*",  # or "*" to allow joining any room
    #         )
    #     ) \
    #  .to_jwt()

    await session.start(
        agent=agent,
        room=ctx.room,
    )

    await session.generate_reply(instructions="سلام! من دستیار صوتی هستم. می‌تونم کمکت کنم؟")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.environ["LIVEKIT_API_KEY"],
            api_secret=os.environ["LIVEKIT_API_SECRET"],
            ws_url=os.environ["LIVEKIT_URL"],
        ))