import json
import sqlite3
from datetime import datetime
from pathlib import Path

JSON_FILE = "reids.json"
SQL_FILE = "redis.sql"
DB_FILE = "redis.db"


def parse_date(raw):
    """Convert date to ISO string format for storage."""
    return datetime.strptime(raw, "%m/%d/%y %H:%M").isoformat()


def load_data(conn, orders):
    cur = conn.cursor()
    for order in orders:
        cur.execute(
            "INSERT INTO orders (order_date) VALUES (?)",
            (parse_date(order["charges"]["date"]),),
        )
        order_id = cur.lastrowid

        c = order["charges"]
        cur.execute(
            "INSERT INTO order_charges (order_id, subtotal, taxes, total) VALUES (?, ?, ?, ?)",
            (order_id, c["subtotal"], c["taxes"], c["total"]),
        )

        for item in order["items"]:
            cur.execute(
                "INSERT INTO order_items (order_id, name, price) VALUES (?, ?, ?)",
                (order_id, item["name"], item["price"]),
            )

        p = order["payment"]
        cur.execute(
            "INSERT INTO order_payments (order_id, method, card_type, last_4_card_number, zip, cardholder) VALUES (?, ?, ?, ?, ?, ?)",
            (
                order_id,
                p.get("method"),
                p.get("card_type"),
                p.get("last_4_card_number"),
                p.get("zip"),
                p.get("cardholder"),
            ),
        )


def main():
    file_path = Path.cwd() / "Data Science" / "Module 2"
    with open(file_path / SQL_FILE, "r") as f:
        schema = f.read()
 
    with open(file_path / JSON_FILE, "r") as f:
        data = json.load(f)

    with sqlite3.connect(file_path / DB_FILE) as conn:
        conn.executescript(schema)
        load_data(conn, data["orders"])
        conn.commit()

    print(f"Done: {len(data['orders'])} orders loaded into {DB_FILE}")


if __name__ == "__main__":
    main()
