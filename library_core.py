import sqlite3
from typing import Any, List, Optional, Tuple


class DatabaseManager:
    """Handles database connection and SQL queries in a secure fashion."""

    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
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


class CLI:
    """Handles UI in the terminal (TUI)."""
