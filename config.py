from dotenv import load_dotenv
import os
# 1. Load environment variables for API keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")