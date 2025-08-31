import os
from dotenv import load_dotenv

load_dotenv()

# App settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM settings
MODEL = os.getenv("model")
BASE_URL = os.getenv("BASE_URL")

# OpenApi Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


required_vars = {
    "GOOGLE_API_KEY": GOOGLE_API_KEY,
    "model": MODEL,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_KEY": SUPABASE_KEY,
}
missing = [k for k, v in required_vars.items() if not v]
if missing:
    raise RuntimeError(f"Missing required environment variables: {missing}")
