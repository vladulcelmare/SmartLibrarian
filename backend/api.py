import backend.config
import backend.utils as utils
from backend.config import Recommendation
from backend.database_load import chromadb_collection, chromadb_client, embed

data = utils.fetch_data() # holds the .json book data as a dictionary for easy access
titles = data.keys() # only titles

def call_function(function_name: str, arguments: dict):
    """
    Calls the appropriate function based on the provided function name and arguments."""
    if function_name == "get_summary_by_title":
        return get_summary_by_title(arguments["title"], arguments.get("history", []))
    
    elif function_name == "get_recommendation":
        return get_recommendation(arguments["question"], arguments.get("top_k") or 3)
    
    # if the chatbot tries using a tool that does not exist
    raise ValueError(f"Unknown function name: {function_name}")

def search_for_books(question: str, top_k: int = 3) -> list[dict]:
    """
    Searches for books in the ChromaDB collection based on the provided question and returns a list of matching books.
    """
    global chromadb_client, chromadb_collection

    # apply embeddings to the question to get a vector representation to search
    query_embedding = embed(question)

    # rag
    results = chromadb_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    matches = []
    # top_k searches
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


def get_recommendation(question: str, history: list[dict[str, str]], top_k: int = 3) -> list[Recommendation]:
    """
    Searches for book recommendations based on the provided question and returns a list of Recommendation objects.
    """
    global data, titles

    # get top_k most relevant books
    matches = search_for_books(question, top_k=top_k)

    # store in recommendations list
    recommendations = []
    if matches:
       
        for match in matches:
            book_title = match["metadata"]["title"].upper()

            # if its a valid title, otherwise we just ignore
            if book_title in titles:
                book_data = data[book_title]

                recommendations.append(Recommendation(
                    title = book_data["pretty_title"],
                    author = book_data["author"],
                    year = book_data["year"],
                    genre = book_data["genre"],
                    themes = book_data["themes"],
                    summary = book_data["summary"],
                ))

    # failsafe
    if recommendations == []:
        recommendations.append(Recommendation(
            answer = "Sorry, I couldn't find any recommendations based on your query. "
            "Please try again with different preferences or a different book."
        ))

    return recommendations

def get_summary_by_title(title: str) -> Recommendation:
    """
    Retrieves the summary and metadata of a book based on the provided title.
    """
    global data, titles

    # take all book titles
    title = title.upper()

    # if its a valid title
    if title in titles:
        book_data = data[title]
        return Recommendation(
            title = book_data["pretty_title"],
            author = book_data["author"],
            year = book_data["year"],
            genre = book_data["genre"],
            themes = book_data["themes"],
            summary = book_data["summary"],
        )

    # failsafe
    return Recommendation(
        answer = "Sorry, I couldn't find a summary for the book you requested. "
        "Please make sure you entered the correct title or try again with a different book."
    )
