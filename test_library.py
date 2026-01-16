import unittest

from library_core import DatabaseManager


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
