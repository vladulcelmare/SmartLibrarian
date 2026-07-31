from pathlib import Path
import json
import chromadb
import hashlib
from backend.config import EMBEDDING_MODEL, openai_client
from backend.utils import fetch_data


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = BASE_DIR / "data" / "book_summaries.json"
CHROMA_DIR = BASE_DIR / "chroma_db"

chromadb_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
chromadb_collection = chromadb_client.get_or_create_collection("sl1_books")

books = fetch_data()


def process_book(book : dict) -> str:
    """
    Processes a book dictionary and returns a formatted string.
    """

    return (
        f"Title: {book['pretty_title']}\n"
        f"Author: {book['author']}\n"
        f"Year: {book['year']}\n"
        f"Genre: {book['genre']}\n"
        f"Themes: {', '.join(book['themes'])}\n"
        f"Summary: {book['summary']}\n"
    )

def embed(text : str):
    """
    Generates an embedding for the given text using the OpenAI API.
    """

    global openai_client
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def make_hash(text : str) -> str:
    """
    Generates a SHA-256 hash for the given text.
    """

    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def modify_db():
    """
    Modifies the ChromaDB collection by processing the books and updating the collection with embeddings and metadata.
    """

    global chromadb_client, chromadb_collection
    global books

    existing = chromadb_collection.get(include=["metadatas"])
    hashed_books = {
        book_id: (metadata or {}).get("hash")
        for book_id, metadata in zip(existing["ids"], existing["metadatas"])
    }

    current_ids = set()
    changed_ids, changed_docs, changed_metadata = [], [], []

    for title, book in books.items():
        current_ids.add(title)
        doc = process_book(book)
        book_hash = make_hash(doc)

        if hashed_books.get(title) != book_hash:
            metadata = {
                "title": book["pretty_title"],
                "author": book["author"],
                "year": book["year"],
                "genre": book["genre"],
                "themes": book["themes"],
                "summary": book["summary"],
                "hash": book_hash
            }
            changed_ids.append(title)
            changed_docs.append(doc)
            changed_metadata.append(metadata)

    if changed_docs:
        changed_embeds = [embed(doc) for doc in changed_docs]

    existing_ids = set(existing["ids"])
    deleted_ids = list(existing_ids - current_ids)

    if deleted_ids:
        chromadb_collection.delete(ids=deleted_ids)

    if changed_docs:
        chromadb_collection.upsert(
            ids = changed_ids,
            documents = changed_docs,
            metadatas = changed_metadata,
            embeddings = changed_embeds
        )

    return chromadb_collection

def search_books(question : str, top_k : int = 3) -> list[dict]:
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

if __name__ == "__main__":
    modify_db()
