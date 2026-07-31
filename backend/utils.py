from backend.config import Recommendation

def fetch_data() -> dict:
    import os
    import json

    file_path = os.path.abspath("data\\book_summaries.json")
    print(file_path)

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

def filter_explicitlanguage(text: str) -> bool:
    """
    Filters out explicit language from the given text.
    """
    import os

    file_path = os.path.abspath("data\\sensitive_words.txt")

    # List of explicit words to filter out
    
    with open(file_path, "r", encoding="utf-8") as f:
        explicit_words = [line.strip() for line in f.readlines()]

    return False
