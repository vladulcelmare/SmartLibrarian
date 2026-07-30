# Smart Librarian

Chatbot specialised in book recommendations. Powered by Streamlit & OpenAI.
Demo project.

# Requirements

The user must have installed : uv, Python, Streamlit, functional OpenAI key.

# Frontend

The interface is fully functional and does not yet depend on OpenAI key.
By running the commands under in the specified order, the user opens the webpage dedicated. Localhost only. All commands are mandatory(pythonpath specifies the path for root directory)

```powershell
cd SmartLibrarian;
uv venv;
uv pip install streamlit openai;
$env:PYTHONPATH = (Get-Location).Path;
uv run --python .venv\Scripts\python.exe streamlit run frontend/app.py
```
