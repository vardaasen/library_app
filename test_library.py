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

    def test_lending_process(self):
        lib = LibrarySystem(self.db)
        # Setup data
        lib.add_book("Clean Code", "Uncle Bob", "999")
        lib.add_member("Per", "per@test.no", "P01")

        # Fetch IDs
        book_id = lib.search_books("Clean Code")[0]["id"]
        member_id = lib.search_members("Per")[0]["id"]

        # 1. Test lending
        success = lib.lend_book(book_id, member_id)
        self.assertTrue(success)

        # 2. Test if book is marked as unavailable
        book_after = lib.search_books("Clean Code")[0]
        self.assertEqual(book_after["status"], "unavailable")

        # 3. Test lending of unavailable book
        success_fail = lib.lend_book(book_id, member_id)
        self.assertFalse(success_fail)

        # 4. Test return book
        lib.return_book(book_id)
        book_final = lib.search_books("Clean Code")[0]
        self.assertEqual(book_final["status"], "available")
