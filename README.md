# Web Search Agent (SearchSavvy)

This project implements a web search agent using the `openai-agents` library, integrated with the Tavily API for web searches and personalized responses based on user profiles. The agent dynamically adjusts its behavior based on user context and query keywords.

## Setup Steps

1. **Install uv**: Ensure you have `uv` installed. If not, install it by following the instructions at [uv documentation](https://docs.astral.sh/uv/).

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/ehtashamtoor/websearch-agent
   cd websearch-agent
   ```

3. **Set Up the Virtual Environment**:
   This project uses `uv` to manage dependencies. Run the following command to create a virtual environment and install dependencies from `pyproject.toml`:

   ```bash
   uv sync
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root directory and add the following environment variables:

   ```bash
   GOOGLE_API_KEY=<your-google-api-key>
   TAVILY_API_KEY=<your-tavily-api-key>
   ```

   - Obtain a Google API key for the Gemini model from [Google Cloud](https://cloud.google.com/).
   - Obtain a Tavily API key from [Tavily](https://tavily.com/).

5. **Activate the Virtual Environment**:
   Activate the virtual environment created by `uv`:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

## How Personalisation Works

The web search agent personalizes responses using a `UserProfile` class defined in `userContext.py`. Here's how it works:

- **User Context**: The `UserProfile` dataclass stores user-specific information such as `name`, `topic` of interest, `city`, and a unique `uid`. This data is used to tailor responses to the user's preferences.
- **Dynamic Instructions**: The `dynamic_instructions` function in `web_search_agent.py` generates instructions for the agent based on the user's profile. For example, it includes the user's name to make responses more engaging and personalized.
- **Query Adjustment**: The agent detects specific keywords (e.g., "deeper", "summarize", "explain", "detailed") in the user's query and adjusts the `max_results` parameter for the `web_search` tool to provide more or fewer results as needed.
- **Mock Data**: The `mockData.py` file contains sample user profiles for testing. The agent uses these profiles to simulate personalized interactions during development or demos.

This approach ensures that the agent's responses are context-aware and relevant to the user's interests and needs.

## How to Run the Demo

1. **Ensure Setup is Complete**: Follow the setup steps above to install dependencies and configure environment variables.

2. **Run the Agent**:
   The demo uses the `web_search_agent.py` script, which now supports continuous user interaction:

   ```bash
   uv run python web_search_agent.py

   ```

3. **Modify the Demo**:

   - To test with different user profiles, edit the `user_profile` selection in the `main()` function of `web_search_agent.py`. For example, change `profiles[1]` to `profiles[0]` to use Alice's profile (Machine Learning).
   - Update the query in the `Runner.run_streamed` call to test different search terms or keywords like "detailed" or "explain".
