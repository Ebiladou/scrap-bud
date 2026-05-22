import os
from dotenv import load_dotenv

load_dotenv()

SCHOOL_NAME = os.getenv("BRI_NAME")
OUTPUT_FILE = os.getenv("BRI_OUTPUT_FILE")
LIST_URL = os.getenv("BRI_LIST_URL")

DELAY = 0.8

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
