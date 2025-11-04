import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "AFIW-ZulfiQode")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
