"""
database/connection.py — MySQL connection management for FitHer Gym Manager.

Provides a context manager that opens a connection and guarantees cleanup.
All SQL queries in this project use parameterized statements to prevent
SQL injection.
"""

import sys
import os
import contextlib
import mysql.connector
from mysql.connector import Error as MySQLError

# Allow imports from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_db_config


def get_connection():
    """
    Open and return a new MySQL connection using credentials from .env.
    The caller is responsible for closing it (prefer the context manager below).
    Raises a clear RuntimeError if the connection fails.
    """
    try:
        cfg = get_db_config()
        conn = mysql.connector.connect(**cfg)
        return conn
    except EnvironmentError as e:
        raise RuntimeError(str(e)) from e
    except MySQLError as e:
        raise RuntimeError(
            f"Could not connect to MySQL: {e}. "
            "Check that MySQL is running and your .env credentials are correct."
        ) from e


@contextlib.contextmanager
def db_connection():
    """
    Context manager that yields an open MySQL connection.
    Commits on clean exit, rolls back on exception, always closes the connection.

    Usage:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


def test_connection() -> tuple[bool, str]:
    """
    Attempt a connection and return (True, version_string) or (False, error_message).
    Safe to call from the UI to show a database status indicator.
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
        return True, f"MySQL {version}"
    except Exception as e:
        return False, str(e)
