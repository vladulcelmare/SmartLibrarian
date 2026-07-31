from pathlib import Path
import json
import unicodedata
from backend.config import Recommendation

def fetch_data() -> dict:
    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = BASE_DIR / "data" / "book_summaries.json"

    data = {}
    data["book_summaries"] = json.load(open(file_path, "r", encoding="utf-8"))

    final_data = {}

    for x in data["book_summaries"]:
        final_data[x["title"].upper()] = {
            "author": x["author"],
            "year": x["year"],
            "genre": x["genre"],
            "themes": x["themes"],
            "summary": x["summary"],
            "pretty_title": x["title"]
        }

    return final_data

def format_answer(x : Recommendation) -> str:
    return (
        x.answer + '\n\n' +
        (f"Title: {x.title}" if x.title else "") +
        (f", Author: {x.author}" if x.author else "") +
        (f" (Released in {x.year})" if x.year else "") + '\n\n' +
        (f"Genre: {x.genre}" if x.genre else "") + '\n\n' +
        (f"Themes: {', '.join(x.themes)}" if x.themes else "") + '\n\n' +
        (f"Summary: {x.summary}" if x.summary else "") +
        (f"Image URL: {x.image_url}" if x.image_url else "")
    )

def filter_explicitlanguage(text : str):
    """
    Filters out explicit language from the given text.
    """

    import re
    import unicodedata

    def normalise_text(text : str) -> str:
        """
        Helper function to normalise text and include unicode characters.
        """

        text = unicodedata.normalize("NFKC", text)
        text = text.casefold()

        words = re.findall(r"\w+", text, flags=re.UNICODE)
        return " ".join(words)


    if text is None:
        return

    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = BASE_DIR / "data" / "sensitive_words.txt"

    text = normalise_text(text)
    
    with open(file_path, "r", encoding="utf-8") as f:
        explicit_words = [normalise_text(line.strip()) for line in f.readlines() if line is not None]

    if isinstance(text, str):
        for word in explicit_words:
            if word == text:
                return True

    elif isinstance(text, list):
        for word in explicit_words:
            if word in text:
                return True
            
    return False
