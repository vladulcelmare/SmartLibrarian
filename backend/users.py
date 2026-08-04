import pyodbc
import os
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime, timedelta

load_dotenv()

def get_connection():
    """
    Establishes a connection to the SQL Server database using the provided environment variables.
    """
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

def ensure_user(user_id: str, username: str, email: str) -> None:
    """
    Create the Google-authenticated user if it does not exist yet.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "IF NOT EXISTS (SELECT 1 FROM users.user_login WHERE userid = ?) INSERT INTO users.user_login (userid, username, user_email) VALUES (?, ?, ?)",
            user_id,
            user_id,
            username,
            email,
        )
        conn.commit()


def new_conversation(user_id: str, title: str = None) -> str:
    """
    Creates a new conversation for the given user and returns the conversation ID.
    """
    conversation_id = str(uuid4())

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats.conversations (userid, conversation_id, title, creation_date) VALUES (?, ?, ?, ?)",
            user_id,
            conversation_id,
            title,
            datetime.now()
        )
        
        conn.commit()

    return conversation_id

def add_message(conversation_id: str, message: str, role: str) -> None:
    """
    Adds a message to the specified conversation in the database.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats.messages (conversation_id, content, chat_role) VALUES (?, ?, ?)",
            conversation_id,
            message,
            role
        )
        
        conn.commit()


def retrieve_conversation(user_id: str, days: int = 7) -> list[tuple[str, str, datetime]]:
    current_date = datetime.now() - timedelta(days=days)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT conversation_id, title, creation_date FROM chats.conversations WHERE userid = ? AND creation_date >= ? ORDER BY creation_date DESC",
            user_id,
            current_date
        )
        conversations = cursor.fetchall()

    return conversations

def load_conversation(conversation_id: str) -> list[tuple[str, str]]:
    """
    Loads the messages of a specific conversation from the database.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content, chat_role FROM chats.messages WHERE conversation_id = ? ORDER BY message_id ASC",
            conversation_id
        )
        messages = cursor.fetchall()

    return messages

def delete_conversation(conversation_id: str) -> None:
    """
    Deletes a specific conversation and its associated messages from the database.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM chats.messages WHERE conversation_id = ?",
            conversation_id
        )
        cursor.execute(
            "DELETE FROM chats.conversations WHERE conversation_id = ?",
            conversation_id
        )
        
        conn.commit()