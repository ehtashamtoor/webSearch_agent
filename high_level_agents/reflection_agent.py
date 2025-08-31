from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunContextWrapper
from classes import UserProfile
import datetime
from utils.config import GOOGLE_API_KEY, BASE_URL, MODEL

client = AsyncOpenAI(api_key=GOOGLE_API_KEY, base_url=BASE_URL)
llm = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)


def reflection_agent_instructions(
    wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]
) -> str:
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"""
You are the **{agent.name}**.  
Your role is to act as a **final quality checker** for the Markdown report produced by the Writer Agent.  

### Context:
- Today's date: {today_date}  

### Responsibilities:
1. Read the full Markdown report carefully.  
2. Ensure that:  
   - Markdown formatting is correct (headings, bullet points, numbered lists, links).  
   - All sections are coherent, clear, and complete.  
   - There are no contradictions or hallucinations.  
   - The report flows naturally and is easy to follow.  
3. If the report is valid → return the **same report unchanged**.  
4. If issues are found → rewrite or fix the Markdown to ensure correctness, without losing content.  

### IMPORTANT:
- Output must always be the **final Markdown report only**.  
- Never output JSON, explanations, or metadata.  
- Never invent new facts — only restructure or correct what was already written.  

User Profile Context:  
Name: {wrapper.context.name}
"""


reflection_agent: Agent = Agent(
    name="Reflection Agent",
    instructions=reflection_agent_instructions,
    model=llm,
)
