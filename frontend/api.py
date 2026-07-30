from dataclasses import dataclass
from backend import utils


data = utils.fetch_data()
titles = data.keys()


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


def get_recommendation(question: str, history: list[dict[str, str]]) -> Recommendation:
    global data, titles

    question = question.upper()

    if question in titles:
        return Recommendation(
            answer=f"I've found a book that matches your query!",
            title=data[question.upper()]["pretty_title"],
            author=data[question.upper()]["author"],
            year=data[question.upper()]["year"],
            genre=data[question.upper()]["genre"],
            themes=data[question.upper()]["themes"],
            summary=data[question.upper()]["summary"]
        )

    return Recommendation(
        answer="Sorry, I couldn't find a book that matches your query. " \
        "Please try again with different keywords or ask for a recommendation based on a specific genre or theme."
    )

def get_summary_by_title(title: str) -> Recommendation:
    global data, titles

    title = title.upper()

    if title in titles:
        return Recommendation(
            answer = "Sure! Here's a summary of the book you requested:",
            title = data[title.upper()]["pretty_title"],
            author = data[title.upper()]["author"],
            summary = data[title.upper()]["summary"]
        )
    
    return Recommendation(
            answer = "Sorry, I couldn't find a summary for the book you requested. " \
            "Please make sure you entered the correct title or try again with a different book."
    )