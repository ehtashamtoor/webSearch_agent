from agents import Runner, InputGuardrailTripwireTriggered
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from mockData import profiles
from classes import UserProfile
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel
from supabase_session import SupabaseSession
from logger_colors import BLUE, GREEN, RED, RESET
from high_level_agents.requirement_gathering_agent import requirement_gathering_agent

# FastAPI app
app = FastAPI(
    title="Deep Research Agent System",
    description="A deep research agent system that helps you in finding and researching about your Learning Goals roadmaps, topics, courses, videos, articles etc",
)


async def stream_agent_response(
    query: str, user_profile: UserProfile
) -> AsyncGenerator[str, None]:
    session = SupabaseSession(session_id=user_profile.uid)
    try:
        result = Runner.run_streamed(
            requirement_gathering_agent,
            query,
            context=user_profile,
            session=session,
            max_turns=50,
        )
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                yield event.data.delta
    except InputGuardrailTripwireTriggered:
        print("Trip wire triggered")
    except Exception as e:
        print(f"{RED}Unexpected error in stream_agent_response: {e}{RESET}")
        yield "⚠️ An unexpected error occurred. Please try again later."


@app.get("/system-health")
async def system_health():
    """Endpoint to check the health of the system"""

    return {"status": "System is online"}


class ChatQueryRequest(BaseModel):
    query: str
    uid: str


@app.post("/chat", tags=["Agent Chat"])
async def chat(req: ChatQueryRequest):
    print(f"{BLUE} request data{RESET}=>", req)
    query = req.query.strip()
    uid = req.uid.strip()

    if not query:
        return {"error": "Query cannot be empty."}
    if not uid:
        return {"error": "User ID cannot be empty."}

    # Get user profile (mocked from list)
    profile_data = next((p for p in profiles if p["uid"] == uid), None)
    if not profile_data:
        return {"error": "Invalid user ID."}

    user_profile = UserProfile(
        profile_data["name"], profile_data["city"], profile_data["uid"]
    )

    return StreamingResponse(
        stream_agent_response(query, user_profile),
        media_type="text/event-stream",  # For SSE
    )
