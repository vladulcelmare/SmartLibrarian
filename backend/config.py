"""
Configuration settings and constants for the Smart Librarian application.
This module defines constants, data classes, and configuration settings used throughout the application.
It includes the OpenAI client, embedding and chat models, and the system prompt for the chatbot.
"""

from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-5.6-luna"

load_dotenv(BASE_DIR / ".env")
openai_client = OpenAI()


@dataclass
class Recommendation:
    answer: str | None = None
    title: str | None = None
    author: str | None = None
    year: int | None = None
    genre: str | None = None
    themes: list[str] | None = None
    summary: str | None = None
    image_url: str | None = None

CHAT_TOOLS = [
    {
        "type": "function",
        "name": "get_summary_by_title",
        "description":(
            "Only use this when the user asks for a specific book title."
            "Returns the summary and metadata of the book title if found."
            "If the book is not found, return a message indicating that the book was not found."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title or approximate title of a book"
                }
            },
            "required": ["title"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_recommendation",
        "description": (
            "Searches the local book database for books matching the user's preferences, themes, genre, or description."
            "Returns a list of recommendations. Each list item contains the book's title, author, year, genre, themes, and summary."
            "If no books are found, the list contains one fallback item with an answer and empty book metadata."),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's book preferences or request."
                },
                "top_k": {
                    "type": ["integer", "null"],
                    "description": "Maximum number of books to return.",
                    "minimum": 1,
                    "maximum": 5
                }
        },
        "required": ["question", "top_k"],
        "additionalProperties": False
    },
    "strict": True
}
]

SYSTEM_PROMPT = """
You are Smart Librarian, a book recommendation assistant.

Your scope is strictly limited to:
- recommending books from the local database;
- summarizing books from the local database;
- discussing books, authors, genres, themes, and reading preferences.

Use the available tools whenever the user asks for a recommendation or book summary.
Use only information returned by the local tools.
Never invent books, summaries, authors, or metadata.

If the user asks a non-book question, such as physics, politics, coding,
medicine, or general knowledge, do not answer that question.
Reply only:
"I can help with book recommendations and summaries. Please ask me about a book,
genre, author, or reading preference."

A question about a book involving physics is allowed.
A general question about any topic which does not involve books is not allowed.
If the user insists on asking a non-book question, politely decline.
Every answer must be book-related and you should always end with a follow-up question.
The get_recommendation tool returns a list. Treat every list item as a separate recommendation and include every returned book.
Preserve the title, author, year, genre, themes, and summary returned by the tools.
If a tool returns a fallback answer with empty book metadata, return that answer exactly and do not invent a book.
"""
