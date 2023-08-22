import os
import tempfile
import unittest

from databases import DatabaseColInfo
from databases import SQLite3Database

DB_FILE = os.path.join(tempfile.gettempdir(), 'test_db.db')  # sqlite3')
TABLE_NAME = 'organisations'
COL1 = 'organisation_name'
COL2 = 'url'
COL1_DATA = DatabaseColInfo(COL1, 'TEXT', 'PRIMARY KEY')
COL2_DATA = DatabaseColInfo(COL2, 'TEXT', 'UNIQUE')


def table_exists(db, table_name):
    # Helper method to check if a table exists in the database
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = db.connection.execute(query, (table_name,)).fetchone()
    if result is None:
        return False
    else:
        return True


class TestSQLite3DatabaseCreation(unittest.TestCase):

    def setUp(self):
        self.db = SQLite3Database(DB_FILE)

    def tearDown(self):
        if self.db.connection:
            self.db.disconnect()
            os.remove(DB_FILE)

    def test_connect_disconnect(self):
        self.db.connect()
        self.assertIsNotNone(self.db.connection)
        self.db.disconnect()
        self.assertIsNone(self.db.connection)

    def test_connect_twice(self):
        self.db.connect()
        self.assertIsNotNone(self.db.connection)
        self.db.connect()
        self.assertIsNotNone(self.db.connection)

    def test_disconnect_twice(self):
        self.db.connect()
        self.assertIsNotNone(self.db.connection)
        self.db.disconnect()
        self.assertIsNone(self.db.connection)
        self.db.disconnect()
        self.assertIsNone(self.db.connection)

    def test_create_table(self):
        self.db.connect()
        self.db.create_table(TABLE_NAME, COL1_DATA, COL2_DATA)
        self.assertTrue(table_exists(self.db, TABLE_NAME))


class TestSQLite3DatabaseManipulation(unittest.TestCase):
    def setUp(self):
        self.db = SQLite3Database(DB_FILE)
        self.db.connect()
        self.db.create_table(TABLE_NAME, COL1_DATA, COL2_DATA)
        self.db.insert(TABLE_NAME, {COL1: "ABB B.V.", COL2: "www.abb.com"})
        self.db.insert(TABLE_NAME, {COL1: "BK", COL2: "www.bk.com"})
        self.db.insert(TABLE_NAME, {COL1: "KFC", COL2: "www.kfc.com"})

    def tearDown(self):
        if self.db.connection:
            self.db.disconnect()
            os.remove(DB_FILE)

    def test_get_column_values(self):
        organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.assertEqual(["ABB B.V.", "BK", "KFC"], organisations)

    def test_insert(self):
        new_entry_name = "New entry"
        new_entry_url = "www.new.com"
        initial_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.db.insert(TABLE_NAME, {COL1: new_entry_name, COL2: new_entry_url})
        updated_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.assertEqual(len(updated_organisations), len(initial_organisations) + 1)
        added_organisation = set(updated_organisations) - set(initial_organisations)
        self.assertEqual(new_entry_name, *added_organisation)
        new_row = self.db.get_row_containing_term(TABLE_NAME, new_entry_name)
        self.assertEqual(new_entry_url, new_row[COL2])

    def test_insert_duplicate(self):
        initial_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.db.insert(TABLE_NAME, {COL1: "ABB B.V.", COL2: "www.abb.com"})
        updated_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.assertEqual(initial_organisations, updated_organisations)

    def test_delete_by_string_match(self):
        initial_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.db.delete_by_string_match(TABLE_NAME, "BK")
        updated_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.assertEqual(len(updated_organisations), len(initial_organisations) - 1)
        removed_organisation = set(initial_organisations) - set(updated_organisations)
        self.assertEqual("BK", *removed_organisation)

    def test_delete_by_string_match_partial_match(self):
        initial_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.db.delete_by_string_match(TABLE_NAME, "ABB")
        updated_organisations = self.db.get_column_values(TABLE_NAME, COL1)
        self.assertEqual(initial_organisations, updated_organisations)

    def test_get_row_containing_terms(self):
        row_data = self.db.get_row_containing_term(TABLE_NAME, 'BK')
        self.assertEqual({'organisation_name': 'BK', 'url': 'www.bk.com'}, row_data)

    def test_get_non_existing_row_containing_terms(self):
        row_data = self.db.get_row_containing_term(TABLE_NAME, 'BKG')
        self.assertEqual(None, row_data)

    def test_get_primary_key(self):
        primary_key_column = self.db._get_primary_key_column(TABLE_NAME)
        self.assertEqual(COL1, primary_key_column)

    def test_update_row(self):
        org_to_update = "KFC"
        initial_url = self.db.get_row_containing_term(TABLE_NAME, org_to_update)
        self.db.update_row(TABLE_NAME, org_to_update, {COL2: "www.kfc_rocks.com"})
        updated_url = self.db.get_row_containing_term(TABLE_NAME, org_to_update)
        self.assertNotEqual(initial_url, updated_url)
        self.assertEqual("www.kfc_rocks.com", updated_url[COL2])


if __name__ == '__main__':
    unittest.main()
