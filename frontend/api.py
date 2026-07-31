import backend.utils as utils
from backend.config import Recommendation
from backend.database_load import chromadb_collection, chromadb_client, embed

data = utils.fetch_data()
titles = data.keys()

def search_for_books(question : str, top_k : int = 3) -> list[dict]:
    global chromadb_client, chromadb_collection

    query_embedding = embed(question)

    results = chromadb_collection.query(
        query_embeddings = [query_embedding],
        n_results = top_k,
    )

    matches = []

    for i in range(len(results["ids"][0])):
        matches.append(
            {
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return matches

def get_recommendation(question : str, history : list[dict[str, str]]) -> Recommendation:
    global data, titles

    matches = search_for_books(question, top_k = 3)

    if matches:
        # we will just return the first match for now, but we can improve this later
        match = matches[0]
        book_title = match["metadata"]["title"].upper()

        if book_title in titles:
            book_data = data[book_title]

            return Recommendation(
                answer = "Sure! Here's a recommendation based on your query:",
                title = book_data["pretty_title"],
                author = book_data["author"],
                year = book_data["year"],
                genre = book_data["genre"],
                themes = book_data["themes"],
                summary = book_data["summary"]
            )
    return Recommendation(
        answer = "Sorry, I couldn't find a book that matches your query. " \
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
