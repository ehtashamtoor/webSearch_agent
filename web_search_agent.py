import os, asyncio
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool, ModelSettings, RunContextWrapper, ItemHelpers
from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from mockData import profiles
from userContext import UserProfile
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()

# Color codes for terminal output styling
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Disabling tracing
set_tracing_disabled(disabled=True)

google_key = os.getenv("GOOGLE_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

# Setting the OpenAI client
client: AsyncOpenAI = AsyncOpenAI(
    api_key=google_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# setting the LLM model using OPenAIChatCompletionsModel
llm: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client
)
# Setting the Tavily Client
tavily_client = AsyncTavilyClient(api_key=tavily_key)

# TOOLS -------------- Start -----------------
@function_tool
async def web_search(wrapper: RunContextWrapper[UserProfile], query: str, max_results: int = 2) -> dict:
  """A tool to search the web using Tavily API.
  Args:
      wrapper (RunContextWrapper[UserProfile]): The context wrapper containing user profile.
      query (str): The search query.
      max_results (int, optional): The maximum number of results to return. Defaults to 2.
  Returns: 
      dict: The search results from Tavily API.
  """
  
  try:
    if not query or not query.strip():
          print(f"{RED}Error: Query cannot be empty. {RESET}")
          return {"results": [], "error": "Empty Query"}
  
    print(f"{BLUE}Tavily tool query >> {RESET} \n {query} {RESET} \n with max_results: {max_results}")
    
    search_result = await tavily_client.search(query=query, max_results=max_results)
    
    if not search_result['results']:
        print(f"{RED} No results returned from Tavily for query: {RESET} {query}")
        return {"results": [], "error": "No results found"}
    
    return search_result

  except Exception as e:
    error_msg = f"Tavily API error: {str(e)}"
    print(f"{RED}{error_msg}{RESET}")
    return {"results": [], "error": error_msg}

# TOOLS -------------- End -------------------


# cache for LLM responses: {cache_key: {"response": str}}
llm_response_cache = {}


# Dynamic instructions for the agent to change based on user profile
def dynamic_instructions(
    wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]
) -> str:
    return f"""You are a helpful assistant named {agent.name} who is expert in web search. You are helping {wrapper.context.name}. 
    
    Detect Keywords like deeper, explain, detailed, etc. in the query and adjust max_results(default is 2) in the web search tool accordingly.
  
    IMPORTANT: 
    1. Always give the response in a markdown format for headings, links etc.
    2. Be friendly and engaging, as you are assisting {wrapper.context.name}."""

# Creating Our Agent
webSearch_agent: Agent = Agent(
  name="SearchSavvy",
  instructions=dynamic_instructions, 
  model=llm,
  tools=[web_search],
  model_settings=ModelSettings(
    temperature=0.2,
    max_tokens=1000
    )
)

async def main():
    """
    Main function to run the web search agent.
    """
    # Getting a hardcoded user profile from mock data
    user_profile = UserProfile(profiles[1]["name"], profiles[1]["topic"],profiles[1]["city"], profiles[1]["uid"])

    while True:
        # Get user input synchronously using run_in_executor to avoid blocking asyncio
        loop = asyncio.get_event_loop()
        query = await loop.run_in_executor(None, input, f"{BLUE}Enter your query (or type 'exit'/'goodbye' to quit): {RESET}")
        
        # query cannot be empty
        if not query.strip():
            print(f"{RED} Error: Query cannot be empty. Please ask something! {RESET}")
            continue
        # Check for exit conditions
        if query.lower().strip() in ["exit", "goodbye"]:
            print(f"{GREEN}Goodbye, {user_profile.name}!{RESET}")
            break

        # Create cache key based on user ID and query
        cache_key = f"{user_profile.uid}:{query}"
        
        # Check if the response is already cached
        if cache_key in llm_response_cache:
            cached = llm_response_cache[cache_key]
            print(f"{GREEN}Cache hit for query: {RESET} {query}")
            print(f"{BLUE}-- Cached LLM Response: {RESET}\n{cached['response']}")
            print(f"{GREEN}=== Run complete (from cache) ==={RESET}")
            continue

        # Running the agent workflow with the context of the user 
        result: Runner = Runner.run_streamed(webSearch_agent, query, context=user_profile)
        
        final_response = ""
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                final_response += event.data.delta
                print(event.data.delta, end="", flush=True)
        
        # Streaming the stream response types
        # async for event in result.stream_events():
        #     if event.type == "raw_response_event":
        #         continue
        #     elif event.type == "agent_updated_stream_event":
        #         print(f"{BLUE}Agent updated: {RESET} {event.new_agent.name}")
        #         continue
        #     elif event.type == "run_item_stream_event":
        #         if event.item.type == "tool_call_item":
        #             print(f"{BLUE}-- Tool was called {RESET}", event.item.raw_item.name)
        #         elif event.item.type == "tool_call_output_item":
        #             print(f"{BLUE}-- Tool output: {RESET} {event.item.output}")
        #         elif event.item.type == "message_output_item":
        #             response_text = ItemHelpers.text_message_output(event.item)
        #             print(f"{BLUE}-- Message output: {RESET}\n{response_text}")
        #             final_response += response_text
        #         else:
        #             pass  # Ignore other event types

        # Caching the final LLM response if it exists
        if final_response:
            llm_response_cache[cache_key] = {"response": final_response}
            print(f"{GREEN}Cached LLM response for query: {RESET} {query}")

        print(f"{GREEN}=== Run complete ==={RESET}")


# Running our code
asyncio.run(main())