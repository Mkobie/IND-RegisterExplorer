import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path

from logging_config import set_up_logging

LOGGER = set_up_logging()


@dataclass
class DatabaseColInfo:
    """Represents the information needed to define a database column."""
    name: str
    data_type: str
    col_constraint: str


class SQLite3Database:
    """
    Class for working with SQLite3 databases.
    """

    def __init__(self, db_file):
        """
        Initialize the SQLite3Database with the path to the SQLite3 database file.

        :param db_file: Path to the SQLite3 database file.
        """
        self.db_file = db_file
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Connect to the SQLite3 database.
        """
        if not self.connection:
            try:
                self.connection = sqlite3.connect(self.db_file)
                self.cursor = self.connection.cursor()
                LOGGER.info(f"Connected to {self.db_file}")
            except sqlite3.Error as e:
                LOGGER.error("Error connecting to the database:", e)

    def disconnect(self):
        """
        Disconnect from the SQLite3 database.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            LOGGER.info(f"Disconnected from {self.db_file}")

    def create_table(self, table_name: str, *columns: DatabaseColInfo):
        """
        Create a new table in the SQLite3 database, with the provided column setup.

        :param table_name: Name of the table.
        :param columns: The table column information: name, data type, and column constraint.
        """
        all_columns_text = []
        for column in columns:
            column_text = f"{column.name} {column.data_type} {column.col_constraint}"
            all_columns_text.append(column_text)
        all_columns_text = ', '.join(all_columns_text)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({all_columns_text})"

        try:
            self.cursor.execute(query)
            self.connection.commit()
            LOGGER.info(f'Table "{table_name}" created successfully')
        except sqlite3.Error as e:
            LOGGER.error("Error creating table:", e)

    def insert(self, table_name: str, data: dict[str]):
        """
        Insert data into a table in the SQLite3 database.

        :param table_name: Name of the table.
        :param data: A dictionary representing the data to be inserted.
                     Example: {'column_name_1': 'value_1',
                               'column_name_2': 'value_2', ...}
        """
        try:
            placeholders = ', '.join('?' for _ in data.keys())
            query = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({placeholders})"
            try:
                self.connection.execute(query, tuple(data.values()))
            except sqlite3.IntegrityError as e:
                LOGGER.warning(f"Duplicate data not inserted: {e}")
        except sqlite3.Error as e:
            LOGGER.error("Error inserting data:", e)

    def delete_by_string_match(self, table_name: str, target_string: str):
        """
        Delete a row from the specified table where any column matches the target string exactly.

        :param table_name: Name of the table to delete from.
        :param target_string: The exact string to match in any column for deletion.
        """
        try:
            column_names = [column[1] for column in self.cursor.execute(f"PRAGMA table_info({table_name})")]
            placeholders = ' OR '.join([f"{column} = ?" for column in column_names])
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {placeholders}", [target_string] * len(column_names))
            rows_affected = self.cursor.rowcount
            self.connection.commit()

            if rows_affected > 0:
                LOGGER.info(f'Success: Row containing "{target_string}" deleted')
            else:
                LOGGER.info(f'No deletion: Target string "{target_string}" not found')
        except sqlite3.Error as e:
            LOGGER.error("Error deleting data:", e)

    def update_row(self, table_name: str, target_string: str, data_to_update: dict[str]):
        """
        Update a row in the specified table based on the primary key value.

        This method updates a row in the database table based on the primary key value (target string).
        It constructs an SQL UPDATE query to modify the data with the provided values.

        :param table_name: Name of the table to update.
        :param target_string: The primary key value identifying the row to update.
        :param data_to_update: A dictionary containing the column names and their updated values.
                               Example: {'column_name_1': 'value_1',
                                         'column_name_2': 'value_2', ...}
        """
        try:
            primary_key_column = self._get_primary_key_column(table_name)
            set_clause = ', '.join(f"{name} = ?" for name in data_to_update.keys())
            query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_column} = ?"

            param_values = list(data_to_update.values()) + [target_string]

            self.cursor.execute(query, param_values)
            rows_affected = self.cursor.rowcount
            self.connection.commit()

            if rows_affected > 0:
                LOGGER.info(f'Success: Row containing "{target_string}" updated')
            else:
                LOGGER.info(f'No update: Target string "{target_string}" not found')
        except sqlite3.Error as e:
            LOGGER.error("Error updating data:", e)

    def _get_primary_key_column(self, table_name: str) -> str:
        """
        Retrieve the name of the primary key column for the specified table.

        :param table_name: Name of the table to retrieve the primary key column from.
        :return: Name of the primary key column.
        """
        result = self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
        for column in result:
            if column[5]:  # Check if the column is a primary key
                return column[1]
        raise ValueError(f"No primary key found for table '{table_name}'")

    def get_column_values(self, table_name: str, column_name: str) -> list[str]:
        """
        Retrieve values from a specific column in the specified table.

        :param table_name: Name of the table to retrieve values from.
        :param column_name: Name of the column to retrieve values from.
        :return: List of values from the specified column.
                 Example: ['value_1', 'value_2', ...]
        """
        try:
            query = f"SELECT {column_name} FROM {table_name}"
            result = self.cursor.execute(query).fetchall()
            values = [row[0] for row in result]
            return values
        except sqlite3.Error as e:
            LOGGER.error("Error getting column values:", e)

    def get_row_containing_term(self, table_name: str, search_term: str) -> dict[str] or None:
        """
        Retrieve a row containing the specified term from the database table.

        This method searches for a row in the specified table where any column contains
        an exact match to the provided search term. If a matching row is found, its data
        is returned as a dictionary where column names are keys and their values are
        the corresponding data values.

        :param table_name: Name of the table to search in.
        :param search_term: The term to search for in any column.
        :return: A dictionary representing the matching row, or None if not found.
                 Example: {'column_name_1': 'value_1',
                           'column_name_2': 'value_2', ...}
        """
        try:
            column_names = [column[1] for column in self.cursor.execute(f"PRAGMA table_info({table_name})")]
            placeholders = ' OR '.join([f"{column} = ?" for column in column_names])
            query = f"SELECT * FROM {table_name} WHERE {placeholders}"
            result = self.cursor.execute(query, [search_term] * len(column_names)).fetchone()

            if result:
                return dict(zip(column_names, result))
            else:
                return None
        except sqlite3.Error as e:
            LOGGER.error(f'Error getting row containing the term "{search_term}":', e)

    def show_table_data(self, table_name: str):
        """
        Display data from the specified table in a formatted table format.

        :param table_name: Name of the table to display data from.
        """
        try:
            # Execute a query to retrieve all rows from the specified table
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()

            if len(rows) == 0:
                LOGGER.info(f'Table "{table_name}" is empty.')
                return []
            else:
                # Get column names and maximum column widths
                column_names = [description[0] for description in self.cursor.description]
                max_column_widths = [len(name) for name in column_names]

                for row in rows:
                    for i, col in enumerate(row):
                        max_column_widths[i] = max(max_column_widths[i], len(str(col)))

                # Print column names
                print()
                for i, name in enumerate(column_names):
                    print(name.ljust(max_column_widths[i]), end="\t")
                print()  # Print newline after header

                # Print separator line
                separator = "-" * (sum(max_column_widths) + len(column_names) * 4 - 1)
                print(separator)

                # Print each row
                for row in rows:
                    for i, col in enumerate(row):
                        print(str(col).ljust(max_column_widths[i]), end="\t")
                    print()  # Print newline after each row
                print()

        except sqlite3.Error as e:
            LOGGER.error("Error showing table data:", e)


def main():
    db_file = Path(tempfile.gettempdir()) / 'IND-RegisterExplorer.db'
    table_name = 'organisations'
    col1 = 'organisation_name'
    col2 = 'url'
    col1_data = DatabaseColInfo(col1, 'TEXT', 'PRIMARY KEY')
    col2_data = DatabaseColInfo(col2, 'TEXT', 'UNIQUE')

    db = SQLite3Database(db_file)
    db.connect()
    db.create_table(table_name, col1_data, col2_data)
    db.insert(table_name, {col1: "ABB B.V.", col2: "www.abb.com"})
    db.insert(table_name, {col1: "BK", col2: "www.bk.com"})
    db.insert(table_name, {col1: "KFC", col2: "www.kfc.com"})
    list_before_deletion = db.get_column_values(table_name, col1)

    org_to_remove = "ABB B.V."
    removed_organisation_info = db.get_row_containing_term(table_name, org_to_remove)
    db.show_table_data(table_name)
    db.delete_by_string_match(table_name, org_to_remove)
    list_after_deletion = db.get_column_values(table_name, col1)
    removed_organisation = set(list_before_deletion) - set(list_after_deletion)
    LOGGER.info(f"Organisation {removed_organisation} has been deleted. The row data was: {removed_organisation_info}.")
    db.show_table_data(table_name)

    db.update_row(table_name, "KFC", {col2: "www.kfc_rocks.com"})

    db.show_table_data(table_name)

    if db.connection:
        db.disconnect()
        db_file.unlink()
        LOGGER.info(f'Deleted {db_file}')


if __name__ == '__main__':
    main()
