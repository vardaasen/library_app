import sqlite3
from typing import Any, List, Optional, Tuple


class DatabaseManager:
    """Handles database connection and SQL queries in a secure fashion."""

    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self._conn = None

        if self.db_name == ":memory:":
            self._conn = sqlite3.connect(":memory:")
            self._conn.row_factory = sqlite3.Row

        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn:
            return self._conn
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
        conn = self._get_connection()
        conn.execute(schema_members)
        conn.execute(schema_books)
        conn.commit()

        if self.db_name != ":memory:":
            conn.commit()
            conn.close()
        else:
            conn.commit()

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[int]:
        try:
            conn = self._get_connection()
            if self.db_name == ":memory:":
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.lastrowid
            else:
                with conn:
                    cursor = conn.execute(query, params)
                    return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Database error (Integrity): {e}")
            return None
        except sqlite3.Error as e:
            print(f"Generic database error: {e}")
            return None

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        conn = self._get_connection()
        cursor = conn.execute(query, params)
        res = cursor.fetchall()
        if self.db_name != ":memory:":
            conn.close()
        return res

    def close(self):
        """Cleanup"""
        if self._conn:
            self._conn.close()
            self._conn = None


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
