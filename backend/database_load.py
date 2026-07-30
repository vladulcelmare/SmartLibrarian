from pathlib import Path
import json
import chromadb

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = BASE_DIR / "data" / "book_summaries.json"

print(BASE_DIR)
print(DATA_DIR)
print(DATA_FILE)

print("ok")