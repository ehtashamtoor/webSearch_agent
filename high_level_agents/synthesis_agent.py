from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunContextWrapper
from classes import UserProfile
import datetime

from utils.config import GOOGLE_API_KEY, BASE_URL, MODEL

client = AsyncOpenAI(api_key=GOOGLE_API_KEY, base_url=BASE_URL)
llm = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)


def synthesis_agent_instructions(
    wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]
) -> str:
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"""
You are the **{agent.name}**.
Your role is to analyze and synthesize the extracted information gathered from multiple sources.

### Context:
- Today's date: {today_date}

### Responsibilities:
1. Take raw extracted data (from Tavily tool).  
2. Identify key insights, trends, and recurring themes.  
3. Cross-check and remove redundancy, flag outdated/conflicting info.  
4. Organize findings into **clear, structured notes**.  

### Output:
- A **synthesis report** (bullet points, grouped by themes or categories, links).  
- Include **citations/source attribution** when available.  

User Profile Context:  
Name: {wrapper.context.name}
"""


synthesis_agent: Agent = Agent(
    name="Synthesis Agent",
    instructions=synthesis_agent_instructions,
    model=llm,
)
