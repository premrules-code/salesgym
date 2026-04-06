import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STRATEGIES_DIR = os.path.join(DATA_DIR, "strategies")
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
MEMORY_DIR = os.path.join(DATA_DIR, "memory")
VOICE_DIR = os.path.join(DATA_DIR, "voice")
EVALS_DIR = os.path.join(DATA_DIR, "evals")

MAX_TURNS_PER_CALL = 10
STRATEGIES_PER_GENERATION = 8
NUM_CUSTOMER_PERSONAS = 3
DEFAULT_GENERATIONS = 3
