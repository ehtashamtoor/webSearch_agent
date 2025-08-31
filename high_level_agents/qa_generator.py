from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunContextWrapper
from classes import UserProfile
from .models import ResearchPlan
from utils.config import GOOGLE_API_KEY, BASE_URL, MODEL

client = AsyncOpenAI(api_key=GOOGLE_API_KEY, base_url=BASE_URL)
llm = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)


def qg_instructions(
    wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]
) -> str:
    return f"""
You are the **{agent.name}**. Based on previous user requirements,

Produce a JSON output having below fields:
- master_query: one optimized search query.
- refined_queries: 5 distinct optimized sub-queries.

"""


# query_generator_agent = Agent[ResearchPlan](
query_generator_agent = Agent(
    name="Query Generator Agent",
    instructions=qg_instructions,
    model=llm,
    # output_type=ResearchPlan,
)
