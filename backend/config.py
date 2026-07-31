from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-5-nano"

load_dotenv(BASE_DIR / ".env")
openai_client = OpenAI()


@dataclass
class Recommendation:
    answer: str
    title: str | None = None
    author: str | None = None
    year: int | None = None
    genre: str | None = None
    themes: list[str] | None = None
    summary: str | None = None
    image_url: str | None = None
