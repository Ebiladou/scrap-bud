import os
from dotenv import load_dotenv

load_dotenv()

SCHOOL_NAME = os.getenv("MAN_NAME")
OUTPUT_FILE = os.getenv("MAN_OUTPUT_FILE")
LIST_URL    = os.getenv("MAN_LIST_URL")

DELAY = 0.8

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}