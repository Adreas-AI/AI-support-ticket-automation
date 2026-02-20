"""
Database module for Support Ticket Automation API.

Handles:
- SQLite connection
- Database initialization
- Ticket table schema

Safe to run multiple times (idempotent).
"""

import sqlite3
from pathlib import Path

# Project root → /data/tickets.db
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "tickets.db"


def get_connection() -> sqlite3.Connection:
    """
    Return SQLite connection with dict-like row access.
    Ensures /data folder exists.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create database schema if it doesn't exist.
    """

    with get_connection() as conn:

        # ---- tickets table ----
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                source TEXT NOT NULL,
                customer_name TEXT,
                customer_email TEXT,

                subject TEXT NOT NULL,
                body TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'new',
                priority TEXT,
                category TEXT,

                summary TEXT,
                suggested_reply TEXT,

                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )

        # ---- auto update timestamp trigger ----
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS tickets_updated_at
            AFTER UPDATE ON tickets
            FOR EACH ROW
            BEGIN
                UPDATE tickets
                SET updated_at = datetime('now')
                WHERE id = OLD.id;
            END;
            """
        )


if __name__ == "__main__":
    init_db()
    print(f"DB initialized at: {DB_PATH}")
