import sqlite3
import sys
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
                status TEXT DEFAULT 'available',
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

    def lend_book(self, book_id: int, member_id: int) -> bool:
        # 1. Check if book is available
        # Fetch book by ID
        books = self.db.fetch_all("SELECT * FROM books WHERE id = ?", (book_id,))
        if not books:
            return False

        if books[0]["status"] == "unavailable":
            return False

        # 2. Check if member exist
        members = self.db.fetch_all("SELECT * FROM members WHERE id = ?", (member_id,))
        if not members:
            return False

        # 3. Execute loan (update book status and connect to member)
        update_query = (
            "UPDATE books SET status = 'unavailable', borrower_id = ? WHERE id = ?"
        )
        self.db.execute_query(update_query, (member_id, book_id))
        return True

    def return_book(self, book_id: int) -> bool:
        # 1. Check status of book
        books = self.db.fetch_all("SELECT * FROM books WHERE id = ?", (book_id,))
        if not books:
            return False

        if books[0]["status"] == "available":
            return False

        # 2. Reset status and delete connection to member
        update_query = (
            "UPDATE books SET status = 'available', borrower_id = NULL WHERE id = ?"
        )
        self.db.execute_query(update_query, (book_id,))
        return True


class CLI:
    """Handles UI in the terminal (TUI)."""

    def __init__(self):
        self.db = DatabaseManager()
        self.library = LibrarySystem(self.db)

    def display_menu(self):
        print("\n" + "=" * 30)
        print("   LIBRARY SYSTEM v1.0")
        print("=" * 30)
        print("1. Register new book")
        print("2. Register new member")
        print("3. Search for book")
        print("4. Search for member")
        print("5. Lend book")
        print("6. Return book")
        print("7. Exit")
        print("-" * 30)

    def run(self):
        while True:
            self.display_menu()
            choice = input("Select option (1-7): ").strip()

            if choice == "1":
                title = input("Title: ")
                author = input("Author: ")
                isbn = input("ISBN: ")
                if title and author:
                    self.library.add_book(title, author, isbn)
                    print("Book registered.")
                else:
                    print("Error: Title and author are required.")

            elif choice == "2":
                name = input("Name: ")
                email = input("Email: ")
                # Generate default ID if left blank
                default_id = name[:3].upper() + "001" if name else "NEW001"
                member_num = input(f"Member ID (default {default_id}): ") or default_id

                self.library.add_member(name, email, member_num)
                print("Member registered.")

            elif choice == "3":
                term = input("Search (title/author): ")
                results = self.library.search_books(term)
                print(f"\nFound {len(results)} books:")
                for b in results:
                    if b["status"] == "unavailable":
                        status = f"ON LOAN (MemberID: {b['borrower_id']})"
                    else:
                        status = "AVAILABLE"
                    print(f"[ID: {b['id']}] {b['title']} - {b['author']} [{status}]")

            elif choice == "4":
                term = input("Search (name/email): ")
                results = self.library.search_members(term)
                print(f"\nFound {len(results)} members:")
                for m in results:
                    print(f"[ID: {m['id']}] {m['name']} ({m['email']})")

            elif choice == "5":
                try:
                    b_id = int(input("Book ID: "))
                    m_id = int(input("Member ID: "))
                    if self.library.lend_book(b_id, m_id):
                        print("Book lent successfully.")
                    else:
                        print("Error: Could not lend book (already lent/invalid ID).")
                except ValueError:
                    print("Error: ID must be a number.")

            elif choice == "6":
                try:
                    b_id = int(input("Book ID to return: "))
                    if self.library.return_book(b_id):
                        print("Book returned successfully.")
                    else:
                        print(
                            "Error: Could not return book (already available/invalid)."
                        )
                except ValueError:
                    print("Error: ID must be a number.")

            elif choice == "7":
                print("Saving and exiting...")
                sys.exit()
            else:
                print("Invalid choice, please try again.")
