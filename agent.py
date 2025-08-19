

import asyncio
import os
os.environ["LIVEKIT_API_KEY"] = "APIjqSP6tGk2tFD"
os.environ["LIVEKIT_API_SECRET"] = "HUPwC1ijdSVXImU5dGjxxOoyhjufssPUNMX6VSelp9s"
os.environ["LIVEKIT_URL"] = "ws://185.149.192.38:7880"
ROOM_NAME = "default-room"
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


from livekit import api, rtc
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
    client = AsyncOpenAI(base_url="http://ollama.ollama.svc.yarai.local:11434/v1")

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
        open("audio.wav", "wb").write(audio.content)
        logger.info(f"✅ TTS service returned {str(audio)}")
    except Exception as e:
        logger.error(f"❌ TTS connection failed: {e}")


async def list_livekit_rooms(livekit_url: str=os.environ["LIVEKIT_URL"], api_key: str=os.environ["LIVEKIT_API_KEY"], api_secret: str=os.environ["LIVEKIT_API_SECRET"]):
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


async def ensure_room():
    lkapi = api.LiveKitAPI(os.environ["LIVEKIT_URL"], os.environ["LIVEKIT_API_KEY"], os.environ["LIVEKIT_API_SECRET"])
    try:
        # List rooms
        rooms_resp = await lkapi.room.list_rooms(api.ListRoomsRequest())
        room_names = [r.name for r in rooms_resp.rooms]

        if ROOM_NAME in room_names:
            print(f"Room '{ROOM_NAME}' already exists")
        else:
            print(f"Room '{ROOM_NAME}' does not exist — creating")
            await lkapi.room.create_room(api.CreateRoomRequest(name=ROOM_NAME))
            print(f"Room '{ROOM_NAME}' created successfully")
    finally:
        await lkapi.aclose()


async def test_your_agent() -> None:
    async with (
        openai.LLM.with_ollama(
            base_url="http://ollama.ollama.svc.yarai.local:11434/v1",
            model="alibayram/medgemma:latest",
        ) as llm,

        # Create a session for the life of this test. 
        # LLM is not required - it will use the agent's LLM if you don't provide one here
        AgentSession(llm=llm) as session,
    ):
        agent = Agent(
            instructions="تو یه دستیار صوتی هستی که با انسان صحبت میکنه و اون هم با تو صحبت میکنه",
        )
        # Start the agent in the session
        await session.start(agent)
        
        result = await session.run(user_input="سلام")
        logger.info(f"🔍 Result: {result}")



async def entrypoint(ctx: JobContext):

    logger.info("🔍 Testing connections to STT/LLM/TTS services...")
    await ctx.connect()
    
    agent = Agent(
        instructions="تو یه دستیار صوتی هستی که با انسان صحبت میکنه و اون هم با تو صحبت میکنه",
    )

    logger.info("🔍 Testing connections to STT/LLM/TTS services...")

    logger.info("⚡ Now starting AgentSession...")

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(
            base_url="http://my-whisper-service.whisper.svc.yarai.local:9000/api/v1"
        ),
        llm=openai.LLM.with_ollama(
            base_url="http://ollama.ollama.svc.yarai.local:11434/v1",
            model="alibayram/medgemma:latest",
        ),
        tts=openai.TTS(
            base_url="http://172.16.20.10:8080/v1"
        ),
    )

    await session.start(
        agent=agent,
        room=ctx.room,
    )
    logger.info("✅ Agent joined as %s", ctx.room.local_participant.identity)

    @ctx.room.on("participant_connected")
    async def handle_participant(p: rtc.RemoteParticipant):
        await session.say(
            "سلام خیلی خوش آمدید به مکالمه صوتی من",
            allow_interruptions=False,
        )



if __name__ == "__main__":
    # asyncio.run(test_stt())
    # asyncio.run(test_llm())
    asyncio.run(test_tts())
    # asyncio.run(list_livekit_rooms())
    # asyncio.run(ensure_room())
    # asyncio.run(test_your_agent())
    logger.info("🔍 Testing connections to STT/LLM/TTS services... done")
    cli.run_app(WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.environ["LIVEKIT_API_KEY"],
            api_secret=os.environ["LIVEKIT_API_SECRET"],
            ws_url=os.environ["LIVEKIT_URL"],
            port=8989,
        ))