import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / ".nicymage" / "history.db"


def _get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            digest TEXT,
            timestamp TEXT NOT NULL,
            score INTEGER,
            verdict TEXT,
            critical INTEGER,
            high INTEGER,
            medium INTEGER,
            low INTEGER
        )
        """
    )
    return conn


def record_scan(image: str, digest: str, risk: dict, severity_counts: dict, db_path: Path = DB_PATH) -> None:
    conn = _get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT INTO scans (image, digest, timestamp, score, verdict, critical, high, medium, low)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                image,
                digest,
                datetime.now(timezone.utc).isoformat(),
                risk.get("score"),
                risk.get("verdict"),
                severity_counts.get("CRITICAL", 0),
                severity_counts.get("HIGH", 0),
                severity_counts.get("MEDIUM", 0),
                severity_counts.get("LOW", 0),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_history(image: str, db_path: Path = DB_PATH) -> list:
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT timestamp, digest, score, verdict, critical, high, medium, low "
            "FROM scans WHERE image = ? ORDER BY timestamp",
            (image,),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        {
            "timestamp": row[0],
            "digest": row[1],
            "score": row[2],
            "verdict": row[3],
            "critical": row[4],
            "high": row[5],
            "medium": row[6],
            "low": row[7],
        }
        for row in rows
    ]
