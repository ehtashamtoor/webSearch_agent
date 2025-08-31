import datetime
import os, asyncio
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
    RunContextWrapper,
)
from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from classes import UserProfile
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from logger_colors import BLUE, GREEN, RED, RESET
from high_level_agents.qa_generator import query_generator_agent
from high_level_agents.synthesis_agent import synthesis_agent
from high_level_agents.writer_agent import writer_agent
from high_level_agents.reflection_agent import reflection_agent
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

tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)


@function_tool
async def tavily_fetch_and_extract(queries: list[str]) -> list[dict]:
    """
    Perform search, rank results, and extract relevant content in one step.

    Args:
        queries: A list of queries(str)

    Returns:
        A list of extracted data per URL (with title, url, content, etc.)
    """

    print(f"{BLUE} type {RESET}", isinstance(queries, list))
    print(f"{BLUE} Running tavily tool {RESET}", queries)
    # Step 1: Perform searches
    responses = await asyncio.gather(*[tavily_client.search(query=q) for q in queries])

    # Step 2: Filter & collect relevant URLs
    relevant_urls = []
    for response in responses:
        for result in response.get("results", []):
            if result.get("score", 0) > 0.8:  # simple threshold
                relevant_urls.append(result.get("url"))

    print(f"Found {relevant_urls} relevant URLs")
    # Step 3: Extract data from the relevant URLs
    extracted_data = await asyncio.gather(
        *(tavily_client.extract(url) for url in relevant_urls)
    )

    # print(f"{BLUE}extracted data {RESET}", extracted_data)

    return extracted_data


# deep research agent instructions
def deep_research_instructions(
    wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]
) -> str:
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_year = today_date[:4]
    return f"""{RECOMMENDED_PROMPT_PREFIX}
You are the **{agent.name}**.
Your role is to conduct deep research based on the user's requirements gathered by the Requirement Gathering Agent (RG).

### Context:
- Today's date: {today_date}
- Current year: {current_year}

### Style:
You have access to different tools that you can use to enhance your research process. These tools include:

1. **Query Generator Agent**: Helps in creating the master query and generating multiple sub-queries.

2. **Tavily based search tool**: Use this tool to search for information and extract content. You can pass all queries to this tool in one go.

3. **Synthesis Agent**: This agent will help you analyze and synthesize the extracted information into a coherent report.

4. **Writer Agent**: This agent will take the synthesized insights and produce a polished final report for the user.

5. **Reflection Agent**: This agent will act as a final quality checker for the Markdown report produced by the Writer Agent.

### IMPORTANT:
- Respond with the finalized report only in markdown(containing all links, headings, citations etc). No intermediate steps or explanations.
- Donot remove anything important while passing information to other agents like links to the learning materials, citations etc.

User Profile Context:  
Name: {wrapper.context.name}
"""


# Creating Our deep research Agent
deep_research_agent: Agent = Agent(
    name="Deep Research Agent",
    instructions=deep_research_instructions,
    model=llm,
    tools=[
        query_generator_agent.as_tool(
            tool_name="query_generator_agent",
            tool_description="Generates master query and optimized search sub-queries.",
        ),
        tavily_fetch_and_extract,
        synthesis_agent.as_tool(
            tool_name="synthesis_agent",
            tool_description="Analyzes and synthesizes extracted information.",
        ),
        writer_agent.as_tool(
            tool_name="writer_agent",
            tool_description="Generates a polished final report from the synthesized insights.",
        ),
        reflection_agent.as_tool(
            tool_name="reflection_agent",
            tool_description="Acts as a final quality checker for the Markdown report according to the user requirements.",
        ),
    ],
)
