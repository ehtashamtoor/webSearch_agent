# Deep Research Agent System

## 📌 Introduction

The **Deep Research Agent System specialized in helping users with learning and mastering a new skill** is an AI-powered research assistant built with **FastAPI** and a modular chain of specialized agents built using the OPENAI AGENTS SDK. It helps users conduct in-depth research on learning goals, topics, courses, articles, and more.

The system integrates multiple agents:

- **Requirement Gathering Agent** → captures the user's intent and requirements.
- **Deep Research Agent** → orchestrates the research pipeline.
  - **Query Generator Agent** → creates master and sub-queries.
  - **Tavily Search Tool** → fetches and extracts information from the web.
  - **Synthesis Agent** → analyzes and synthesizes the extracted results.
  - **Writer Agent** → generates a polished Markdown report.
  - **Reflection Agent** → reviews and ensures quality of the final output.

The result is a high-quality, citation-rich **Markdown report** streamed back to the user in real time.

---

## ⚙️ Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ehtashamtoor/skill-learn-deep-search-agent.git
cd skill-learn-deep-search-agent
```

### 2. Create Virtual Environment (optional but recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # for Linux/Mac
.venv\Scripts\activate      # for Windows
```

### 3. Install Dependencies

```bash
pip install uv
uv pip install -e .
```

### 4. Environment Variables

Create a **.env** file in the project root with the following values:

```env
HOST=127.0.0.1
PORT=8000

# API Keys
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENAI_API_KEY=your_openai_api_key

# LLM
model=gpt-4o-mini
BASE_URL=https://api.openai.com/v1

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

⚠️ The project will not run if required variables are missing.

---

## 🚀 Running the Project

### Run with Python directly

```bash
uv run python main.py
```

This will start the FastAPI server at:

```
http://127.0.0.1:8000
```

### Available Endpoints

- `` → Health check endpoint.
- `` → Main research endpoint.
  - **Request Body:**
    ```json
    {
      "query": "Best resources to learn deep reinforcement learning",
      "uid": "2"
    }
    ```
  - **Response:** Server-Sent Events (SSE) streaming the research report in Markdown.

---

## ✅ Summary

This project is designed as a **multi-agent deep research system** with real-time streaming responses. It leverages **FastAPI, OpenAI models, Tavily search, and Supabase** to provide structured, reliable research assistance.

You can extend it by:

- Adding new specialized agents.
- Integrating more data sources.
- Enhancing reflection & quality checks.

