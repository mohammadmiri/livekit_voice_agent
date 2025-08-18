

import asyncio
import os
os.environ["LIVEKIT_API_KEY"] = "APIjqSP6tGk2tFD"
os.environ["LIVEKIT_API_SECRET"] = "HUPwC1ijdSVXImU5dGjxxOoyhjufssPUNMX6VSelp9s"
os.environ["LIVEKIT_URL"] = "ws://185.149.192.38:7880"
os.environ["OPENAI_API_KEY"] = ""


import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("livekit").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
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

from openai import AsyncOpenAI


async def test_stt():
    client = AsyncOpenAI(base_url="http://my-whisper-service.whisper.svc.yarai.local:9000/api/v1")

    logger.info("🔍 Testing connections to STT/LLM/TTS services...")

    try:
        file = open("welcome.mp3", "rb")
        result = await client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", file, "audio/wav")
        )
        logger.info(f"✅ STT service responded: {result.text}")
    except Exception as e:
        logger.error(f"❌ STT connection failed: {e}")


async def test_llm():
    client = AsyncOpenAI(base_url="http://ollama.ollama.svc.yarai.local:11434")

    logger.info("🔍 Testing connections to STT/LLM/TTS services...")

    try:
        result = await client.chat.completions.create(
            model="alibayram/medgemma:latest",
            messages=[{"role": "user", "content": "ping"}]
        )
        logger.info(f"✅ LLM service responded: {result.choices[0].message.content}")
    except Exception as e:
        logger.error(f"❌ LLM connection failed: {e}")


async def test_tts():
    client = AsyncOpenAI(base_url="http://172.16.20.10:8080/v1")

    logger.info("🔍 Testing connections to STT/LLM/TTS services...")

    try:
        audio = await client.audio.speech.create(
            model="tts-1",
            input="Hello, world!",
            voice="nova"
        )
        logger.info(f"✅ TTS service returned {len(audio)} bytes")
    except Exception as e:
        logger.error(f"❌ TTS connection failed: {e}")


async def list_livekit_rooms(livekit_url: str=os.environ["LIVEKIT_URL"], api_key: str=os.environ["LIVEKIT_API_KEY"], api_secret: str=os.environ["LIVEKIT_API_SECRET"]):
    """
    Lists all active rooms on a LiveKit server.

    Args:
        livekit_url: The URL of your LiveKit server (e.g., "https://my-project.livekit.cloud").
        api_key: Your LiveKit API key.
        api_secret: Your LiveKit API secret.
    """
    lkapi = api.LiveKitAPI(livekit_url, api_key, api_secret)
    try:
        # Create an empty ListRoomsRequest to get all rooms
        list_rooms_request = api.ListRoomsRequest()
        
        # Call the list_rooms method
        response = await lkapi.room.list_rooms(list_rooms_request)
        
        if response.rooms:
            print("Active LiveKit Rooms:")
            for room in response.rooms:
                print(f"- Name: {room.name}, SID: {room.sid}, Number of Participants: {room.num_participants}")
        else:
            print("No active rooms found on the LiveKit server.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lkapi.aclose()


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
    )

    logger.info("🔍 Testing connections to STT/LLM/TTS services...")

    # test STT
    try:
        stt = openai.STT(
            base_url="http://my-whisper-service.whisper.svc.yarai.local:9000/api/v1"
        )
        result = await stt.transcribe(b"hello")  # minimal audio bytes
        logger.info(f"✅ STT service responded: {result}")
    except Exception as e:
        logger.error(f"❌ STT connection failed: {e}")

    # test LLM
    try:
        llm = openai.LLM.with_ollama(
            base_url="http://ollama.ollama.svc.yarai.local:11434",
        )
        reply = await llm.chat(messages=[{"role": "user", "content": "ping"}])
        logger.info(f"✅ LLM service responded: {reply}")
    except Exception as e:
        logger.error(f"❌ LLM connection failed: {e}")

    # test TTS
    try:
        tts = openai.TTS(
            base_url="http://172.16.20.10:8080/v1"
        )
        audio = await tts.synthesize("ping")
        logger.info(f"✅ TTS service returned {len(audio)} bytes")
    except Exception as e:
        logger.error(f"❌ TTS connection failed: {e}")

    logger.info("⚡ Now starting AgentSession...")

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=stt,
        llm=llm,
        tts=tts,
    )

    await session.start(
        agent=agent,
        room=ctx.room,
    )

    await session.generate_reply(instructions="سلام! من دستیار صوتی هستم. می‌تونم کمکت کنم؟")


if __name__ == "__main__":
    asyncio.run(test_stt())
    asyncio.run(test_llm())
    asyncio.run(test_tts())
    asyncio.run(check_livekit_connection())
    cli.run_app(WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.environ["LIVEKIT_API_KEY"],
            api_secret=os.environ["LIVEKIT_API_SECRET"],
            ws_url=os.environ["LIVEKIT_URL"],
        ))