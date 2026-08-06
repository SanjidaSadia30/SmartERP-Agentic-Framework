import os
from dotenv import load_dotenv

# Environment variables load
load_dotenv()

# Database Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "database", "erp_data.db"))

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# App Configurations
APP_TITLE = "SmartERP Agentic Assistant"
LLM_MODEL = "llama-3.3-70b-versatile"
