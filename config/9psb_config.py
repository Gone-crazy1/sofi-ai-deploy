"""
9PSB API Configuration for Sofi AI
"""

import os
from dotenv import load_dotenv

load_dotenv()

NINEPSB_API_KEY = os.getenv("NINEPSB_API_KEY")
NINEPSB_BASE_URL = os.getenv("NINEPSB_BASE_URL")
