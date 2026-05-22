import os
from dotenv import load_dotenv

load_dotenv()

SCHOOL_NAME = os.getenv("WAR_NAME")
OUTPUT_FILE = os.getenv("WAR_OUTPUT_FILE")
LIST_URL = os.getenv("WAR_LIST_URL")

DELAY = 0.8

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}