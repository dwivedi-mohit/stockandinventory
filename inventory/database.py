import time
import mysql.connector
from mysql.connector import Error as MySQLError
from inventory.config import DB_CONFIG
from inventory.exceptions import DatabaseConnectionError


class DatabaseManager:
    def __init__(self):
        self._connection = None
        self._config = DB_CONFIG.copy()

    def get_connection(self, retries=3, delay=1):
        if self._connection and self._connection.is_connected():
            return self._connection

        last_error = None
        for attempt in range(retries):
            try:
                self._connection = mysql.connector.connect(**self._config)
                self._connection.autocommit = False
                return self._connection
            except MySQLError as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(delay)
                continue

        raise DatabaseConnectionError(
            f"Failed to connect after {retries} attempts: {last_error}"
        )

    def close(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def test_connection(self):
        try:
            conn = self.get_connection()
            return conn.is_connected()
        except DatabaseConnectionError:
            return False

    def execute_query(self, query, params=None, dictionary=False):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=dictionary) if dictionary else conn.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()

    def execute_update(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def execute_many(self, query, params_list):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def execute_procedure(self, procedure_name, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc(procedure_name, params or ())
            return cursor.stored_results()
        finally:
            cursor.close()

    def begin_transaction(self):
        conn = self.get_connection()
        conn.start_transaction()

    def commit(self):
        if self._connection and self._connection.is_connected():
            self._connection.commit()

    def rollback(self):
        if self._connection and self._connection.is_connected():
            self._connection.rollback()
