import datetime, os
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    GuardrailFunctionOutput,
    TResponseInputItem,
    input_guardrail,
)
from classes import UserQuestionGuardRail
from dotenv import load_dotenv
from classes import UserProfile
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from logger_colors import BLUE, GREEN, RED, RESET
from high_level_agents.deep_research_agent import deep_research_agent
from utils.config import GOOGLE_API_KEY, TAVILY_API_KEY, BASE_URL, MODEL

load_dotenv()

google_key = GOOGLE_API_KEY
tavily_key = TAVILY_API_KEY
base_url = BASE_URL

# Setting the OpenAI client
client: AsyncOpenAI = AsyncOpenAI(
    api_key=google_key,
    base_url=base_url,
)

# setting the LLM model using OpenAIChatCompletionsModel
llm: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL, openai_client=client
)

guardrail_agent = Agent(
    name="User Query Validation Agent",
    instructions="Check if the user query is about the deep research topic of learning a new skill.",
    output_type=UserQuestionGuardRail,
    model=llm,
)


@input_guardrail
async def User_Query_Guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    # print(f"{GREEN} Guardrail Result {RESET}=>", result)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_relevant,
    )


# ==========================
# 1. REQUIREMENT GATHERING AGENT
# ==========================


def rg_agent_instructions(
    wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]
) -> str:
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"{GREEN} Today Date {RESET}=>", today_date)
    return f"""{RECOMMENDED_PROMPT_PREFIX}
You are the **Requirement Gathering Agent (RG)**.  
Your role is to collect the learner’s preferences before the Deep Research Agent (DRA) begins.
  
### Context:
- Today's date: {today_date}  
- Keep in mind that the learner may want the **latest resources (2025)** or allow older ones.  

### Your Responsibilities:
1. Review the user’s query (the topic they want to learn).  
2. Ask **up to 4, 5 short clarifying questions** to gather requirements from the user. 
3. If the user is unsure, suggest a reasonable default and move on.  
4. Once you have their answers, stop asking and **handoff to the Deep Research Agent (DRA)** with the user query + requirements.  

### Style:
- Be conversational, natural, and concise.  
- Ask everything in **one turn only** (no long back-and-forth).  
- If the user doesn’t provide enough information, you may ask again **once**.  
- If the user says something like “you decide” or “anything works”, make a **reasonable assumption** and proceed. 
- Use markdown format to ask the user 

User Profile Context:  
Name: {wrapper.context.name}
"""


requirement_gathering_agent: Agent = Agent(
    name="Requirement Gathering Agent",
    instructions=rg_agent_instructions,
    model=llm,
    handoffs=[deep_research_agent],
    input_guardrails=[User_Query_Guardrail],
)
