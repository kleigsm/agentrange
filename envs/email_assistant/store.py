from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY,
    folder TEXT NOT NULL,
    sender TEXT NOT NULL,
    recipients TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    ts TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts (
    name TEXT PRIMARY KEY,
    email TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    start TEXT NOT NULL,
    attendees TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    to_addr TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    ts TEXT NOT NULL
);
"""


class Mailbox:
    """一个 SQLite 假邮箱。每个任务跑之前 reset + seed。"""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def reset(self) -> None:
        self.conn.executescript(
            "DROP TABLE IF EXISTS emails;"
            "DROP TABLE IF EXISTS contacts;"
            "DROP TABLE IF EXISTS events;"
            "DROP TABLE IF EXISTS sent;"
        )
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def seed(self, state: dict[str, Any]) -> None:
        self.reset()
        for e in state.get("emails", []):
            self.conn.execute(
                "INSERT INTO emails(folder, sender, recipients, subject, body, ts)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    e.get("folder", "inbox"),
                    e["sender"],
                    json.dumps(e.get("recipients", []), ensure_ascii=False),
                    e["subject"],
                    e["body"],
                    e.get("ts", ""),
                ),
            )
        for c in state.get("contacts", []):
            self.conn.execute(
                "INSERT OR REPLACE INTO contacts(name, email) VALUES (?, ?)",
                (c["name"], c["email"]),
            )
        self.conn.commit()

    def list_emails(self, folder: str = "inbox") -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, folder, sender, subject, ts FROM emails WHERE folder = ? ORDER BY id",
            (folder,),
        ).fetchall()
        return [dict(r) for r in rows]

    def read_email(self, email_id: int) -> dict[str, Any]:
        row = self.conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
        if row is None:
            raise KeyError(f"email {email_id} not found")
        data = dict(row)
        data["recipients"] = json.loads(data["recipients"])
        return data

    def search_emails(self, query: str) -> list[dict[str, Any]]:
        like = f"%{query}%"
        rows = self.conn.execute(
            "SELECT id, sender, subject, ts FROM emails"
            " WHERE subject LIKE ? OR body LIKE ?"
            " ORDER BY (subject LIKE ?) DESC, id",
            (like, like, like),
        ).fetchall()
        return [dict(r) for r in rows]

    def send_email(self, to: str, subject: str, body: str) -> dict[str, Any]:
        self.conn.execute(
            "INSERT INTO sent(to_addr, subject, body, ts)"
            " VALUES (?, ?, ?, datetime('now'))",
            (to, subject, body),
        )
        self.conn.commit()
        return {"status": "sent", "to": to, "subject": subject}

    def search_contacts(self, query: str) -> list[dict[str, Any]]:
        like = f"%{query}%"
        rows = self.conn.execute(
            "SELECT name, email FROM contacts WHERE name LIKE ? OR email LIKE ?",
            (like, like),
        ).fetchall()
        return [dict(r) for r in rows]

    def create_event(
        self, title: str, start: str, attendees: list[str] | None = None
    ) -> dict[str, Any]:
        self.conn.execute(
            "INSERT INTO events(title, start, attendees) VALUES (?, ?, ?)",
            (title, start, json.dumps(attendees or [], ensure_ascii=False)),
        )
        self.conn.commit()
        return {"status": "created", "title": title, "start": start}

    def sent(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM sent ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self.conn.close()
