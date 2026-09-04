import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.getenv("BOOKING_DB_PATH", "bookings.db"))


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            master TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    return connection


def create_booking(
    user_id: int,
    service: str,
    master: str,
    booking_date: str,
    booking_time: str,
    phone: str,
) -> int:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO bookings (
                user_id, service, master, booking_date, booking_time, phone, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                service,
                master,
                booking_date,
                booking_time,
                phone,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return int(cursor.lastrowid)


def get_active_bookings(user_id: int) -> list[sqlite3.Row]:
    with _connect() as connection:
        return connection.execute(
            """
            SELECT id, service, master, booking_date, booking_time, phone
            FROM bookings
            WHERE user_id = ? AND active = 1
            ORDER BY booking_date, booking_time
            """,
            (user_id,),
        ).fetchall()


def cancel_booking(booking_id: int, user_id: int) -> bool:
    with _connect() as connection:
        cursor = connection.execute(
            """
            UPDATE bookings
            SET active = 0
            WHERE id = ? AND user_id = ? AND active = 1
            """,
            (booking_id, user_id),
        )
        return cursor.rowcount == 1
