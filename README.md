# Smart Librarian

Chatbot specialised in book recommendations. Powered by Streamlit, ChromaDB & OpenAI.
Demo project.


# Requirements

The user must have installed : **uv**, **Python**, **Streamlit**, **ChromaDB**, functional **OpenAI** key.


# Frontend

The interface is fully functional and does not yet depend on OpenAI key.
By running the commands under in the specified order, the user opens the webpage dedicated. Localhost only. All commands are mandatory (pythonpath specifies the path for root directory).

```powershell
cd .\SmartLibrarian
uv venv --python 3.14
uv pip install --python .venv\Scripts\python.exe streamlit openai chromadb
$env:PYTHONPATH = (Get-Location).Path
uv run --python .venv\Scripts\python.exe python -m backend.database_load
uv run --python .venv\Scripts\python.exe streamlit run frontend/app.py
```


# Mentions

This repository uses [github.com/profanity-list](https://github.com/dsojevic/profanity-list/blob/main/en.txt) as data for the explicit language filter, the **en.txt** file having been saved in 
**SmartLibrarian/data/sensitive_words.txt**.
The language used is with no ill intent, only for the sole purpose of ensuring a respectful conversation. Any word/phrase encountered will be met with a polite reply.