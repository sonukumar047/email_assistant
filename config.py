"""
Configuration module for Email Assistant
"""
import os
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Model Configuration
DEFAULT_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3
MAX_TOKENS = 1000

# Tone Styles
ToneStyle = Literal["professional", "friendly", "formal", "casual"]
DEFAULT_TONE: ToneStyle = "professional"

# Intent Categories
VALID_INTENTS = ["complaint", "request", "feedback", "inquiry"]

# Escalation Settings
ESCALATION_KEYWORDS = [
    "urgent", "immediately", "asap", "critical", 
    "billing issue", "payment failed", "refund",
    "terrible", "worst", "angry", "frustrated"
]
REPEAT_THRESHOLD = 2  # Number of interactions before auto-escalation

# Memory Settings
MEMORY_FILE = "data/memory.json"
MAX_HISTORY_LENGTH = 5  # Keep last N interactions

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
