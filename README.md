# Smart Librarian

Chatbot specialised in book recommendations. Powered by Streamlit, ChromaDB & OpenAI. <br>
Demo project written fully in Python 3.13.

# Requirements

The user must have installed the following items :
* **uv**
* **dotenv**
* **Python**
* **Streamlit**
* **ChromaDB**
* **OpenAI** with a functional key.
* **pyodbc**

# Frontend

The interface is built using Streamlit Python package. It features the classic Streamlit interface (including theme selector).<br>
Additions : 
* Left-side sidebar with settings
* User-selection image generation (pending), Speech-To-Text (pending)
* "New conversation" button which resets current chat
* Sample questions
* Text-To-Speech enabled at each reply from the chatbot
* Multilanguage support
* Explicit language filtering

# Backend

Consists of :
* A database built with ChromaDB that stores the user-selected books in .json format, found in **book_summaries.json**
* A second database built with SSMS that logs each new connected user, alongside their complete chat history
* Response loop logic built with OpenAI API consisting of two requests to the model in the **config.py** file
* Response management tools offered to the chatbot such as **get_summary_by_title** and **get_recommendation**
* Other configurations in **config.py**, helper functions in **utils.py**
* Login handled via Google services

# Installation guide

Before executing the commands written bellow, the user must have a functional OpenAI key stored in a .env file. The .env file must be in the same directory as the project (SmartLibrarian).<br>
Recommended : ensure it is in .gitignore, to avoid exposing the key.

```powershell
cd .\SmartLibrarian
uv venv --python 3.13.14
uv pip install --python .venv\Scripts\python.exe streamlit openai chromadb python-dotenv pyodbc "streamlit[auth]"
```

# How to run

```powershell
$env:PYTHONPATH = (Get-Location).Path;
uv run --python .venv\Scripts\python.exe python -m backend.database_load;
uv run --python .venv\Scripts\python.exe streamlit run frontend/app.py;
```

# Mentions

This repository uses [github.com/profanity-list](https://github.com/dsojevic/profanity-list/blob/main/en.txt) as data for the explicit language filter, the **en.txt** file having been saved in 
**SmartLibrarian/data/sensitive_words.txt**.<br>
The language used is with no ill intent, only for the sole purpose of ensuring a respectful conversation. Any word/phrase encountered will be met with a polite reply.<br>
If the user decides to modify the current book database, they must upload the new data in a .json file in the data directory. Any other format is not compatible.<br>
The user must have setup a local database in SSMSS that copies the content of the file **xx** and must have a local container hosted to connect to it. In order to connect, the user must manage the file **secrets.toml** and add the location of the database alongside other details in the **.env** file. Ensure these are added in .gitignore.
