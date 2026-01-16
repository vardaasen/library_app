import sqlite3
from typing import Any, List, Optional, Tuple


class DatabaseManager:
    """Handles database connection and SQL queries in a secure fashion."""

    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self._conn = None
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self) -> None:
        schema_members = """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                member_number TEXT UNIQUE
            );
        """
        schema_books = """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                status TEXT DEFAULT 'ledig',
                borrower_id INTEGER,
                FOREIGN KEY(borrower_id) REFERENCES members(id)
            );
        """
        with self._get_connection() as conn:
            conn.execute(schema_members)
            conn.execute(schema_books)

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[int]:
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()


class LibrarySystem:
    """Business logic for library."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def add_book(self, title: str, author: str, isbn: str) -> None:
        query = "INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)"
        self.db.execute_query(query, (title, author, isbn))

    def add_member(self, name: str, email: str, member_number: str) -> None:
        query = "INSERT INTO members (name, email, member_number) VALUES (?, ?, ?)"
        self.db.execute_query(query, (name, email, member_number))

    def search_books(self, term: str) -> List[sqlite3.Row]:
        query = "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?"
        s_term = f"%{term}%"
        return self.db.fetch_all(query, (s_term, s_term))

    def search_members(self, term: str) -> List[sqlite3.Row]:
        query = "SELECT * FROM members WHERE name LIKE ? OR email LIKE ?"
        s_term = f"%{term}%"
        return self.db.fetch_all(query, (s_term, s_term))


class CLI:
    """Handles UI in the terminal (TUI)."""
