import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
INSTAGRAM_HANDLE = os.getenv("INSTAGRAM_HANDLE", "@words__of__becoming")
PAGE_ID = os.getenv("PAGE_ID", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODELS = [
    "minimax/minimax-m3.1-flash:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "nvidia/nemotron-3.5-lightning:free"
]

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")

POSTING_TIMES = [t.strip() for t in os.getenv("POSTING_TIMES", "08:00,11:30,14:30,18:00,21:30").split(",")]
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

OUTPUT_DIR = BASE_DIR / "generated_cards"
OUTPUT_DIR.mkdir(exist_ok=True)

DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "agent_data.db")))
