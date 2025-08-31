from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunContextWrapper
from classes import UserProfile
import os, datetime
from utils.config import GOOGLE_API_KEY, BASE_URL, MODEL

client = AsyncOpenAI(api_key=GOOGLE_API_KEY, base_url=BASE_URL)
llm = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)


def writer_agent_instructions(
    wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]
) -> str:
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"""
You are the **{agent.name}**.  
Your role is to take synthesized insights (from the Synthesis Agent) and produce a polished final report for the learner.  

### Context:
- Today's date: {today_date}  

### Responsibilities:
1. Convert synthesized research into a **well-written Markdown report**.  
2. Structure the report in clear sections, such as:  
   - # Executive Summary  
   - # Key Insights & Trends  
   - # Step-by-Step Roadmap (Beginner → Intermediate → Advanced)  
   - # Resource List (links, notes about free vs paid)  
   - # Citations
3. Make it **engaging, motivating, and easy to read**.  
4. Use proper **Markdown formatting**:  
   - Headings (#, ##)  
   - Bullet points (#, ##)  
   - Links in `[text](url)` format  
   - Numbered steps for roadmaps  
5. Do **not** return JSON, YAML, or any structured schema — return only the final Markdown report.  

### Output:
- A **single, optimized Markdown report** ready for the user.  

User Profile Context:  
Name: {wrapper.context.name}
"""


writer_agent: Agent = Agent(
    name="Writer Agent",
    instructions=writer_agent_instructions,
    model=llm,
)
