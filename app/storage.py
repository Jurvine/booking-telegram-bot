import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.getenv("BOOKING_DB_PATH", "bookings.db"))
MASTERS = ("Алексей", "Михаил")
ANY_MASTER = "Любой мастер"


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
) -> tuple[int, str] | None:
    with _connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        assigned_master = master
        if master == ANY_MASTER:
            assigned_master = next(
                (
                    candidate
                    for candidate in MASTERS
                    if _slot_is_free(
                        connection, candidate, booking_date, booking_time
                    )
                ),
                "",
            )
            if not assigned_master:
                return None
        elif not _slot_is_free(connection, master, booking_date, booking_time):
            return None

        cursor = connection.execute(
            """
            INSERT INTO bookings (
                user_id, service, master, booking_date, booking_time, phone, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                service,
                assigned_master,
                booking_date,
                booking_time,
                phone,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return int(cursor.lastrowid), assigned_master


def _slot_is_free(
    connection: sqlite3.Connection,
    master: str,
    booking_date: str,
    booking_time: str,
) -> bool:
    occupied = connection.execute(
        """
        SELECT 1
        FROM bookings
        WHERE booking_date = ?
          AND booking_time = ?
          AND active = 1
          AND master IN (?, ?)
        LIMIT 1
        """,
        (booking_date, booking_time, master, ANY_MASTER),
    ).fetchone()
    return occupied is None


def is_slot_available(master: str, booking_date: str, booking_time: str) -> bool:
    with _connect() as connection:
        if master == ANY_MASTER:
            return any(
                _slot_is_free(connection, candidate, booking_date, booking_time)
                for candidate in MASTERS
            )
        return _slot_is_free(connection, master, booking_date, booking_time)


def get_unavailable_times(master: str, booking_date: str) -> set[str]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT booking_time, master
            FROM bookings
            WHERE booking_date = ? AND active = 1
            """,
            (booking_date,),
        ).fetchall()

    if master != ANY_MASTER:
        return {
            row["booking_time"]
            for row in rows
            if row["master"] in (master, ANY_MASTER)
        }

    unavailable = set()
    for booking_time in {row["booking_time"] for row in rows}:
        occupied_masters = {
            row["master"] for row in rows if row["booking_time"] == booking_time
        }
        if ANY_MASTER in occupied_masters or all(
            candidate in occupied_masters for candidate in MASTERS
        ):
            unavailable.add(booking_time)
    return unavailable


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
