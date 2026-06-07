PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS orders (
    order_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS order_charges (
    charge_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL UNIQUE,
    subtotal   REAL    NOT NULL,
    taxes      REAL    NOT NULL,
    total      REAL    NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    price      REAL    NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS order_payments (
    payment_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id           INTEGER NOT NULL UNIQUE,
    method             TEXT    NOT NULL,
    card_type          TEXT,
    last_4_card_number TEXT,
    zip                TEXT,
    cardholder         TEXT,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);
