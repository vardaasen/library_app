import unittest

from library_core import DatabaseManager, LibrarySystem


class TestLibrarySystem(unittest.TestCase):
    def setUp(self):
        # Using :memory: for fast test without files
        self.db = DatabaseManager(":memory:")

    def test_database_tables_exist(self):
        # Check if 'books' table exist
        res = self.db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='books';"
        )
        self.assertIsNotNone(res)

        # Check if 'members' table exist
        res_members = self.db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='members';"
        )
        self.assertIsNotNone(res_members)

    def test_add_and_find_book(self):
        lib = LibrarySystem(self.db)
        lib.add_book("TDD with Python", "Ola Nordmann", "123-456")

        books = lib.search_books("TDD")
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["title"], "TDD with Python")

    def test_add_and_find_member(self):
        lib = LibrarySystem(self.db)
        lib.add_member("Kari Nordmann", "kari@test.no", "KN001")

        members = lib.search_members("Kari")
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["email"], "kari@test.no")
