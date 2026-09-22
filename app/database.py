import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "aquarium.db"


DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    connection = get_connection()

    try:

        # ================================================
        # SITES
        # ================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                location TEXT,

                code TEXT NOT NULL UNIQUE,

                active INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ================================================
        # USERS
        # ================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL UNIQUE,

                password_hash TEXT NOT NULL,

                role TEXT NOT NULL,

                site_id INTEGER,

                active INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (site_id)
                    REFERENCES sites(id)
            )
            """
        )

        # ================================================
        # DEVICES
        # ================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                site_id INTEGER NOT NULL,

                device_code TEXT NOT NULL UNIQUE,

                name TEXT NOT NULL,

                last_seen TEXT,

                active INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (site_id)
                    REFERENCES sites(id)
            )
            """
        )

        # ================================================
        # FISHES
        # ================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                site_id INTEGER NOT NULL,

                filename TEXT NOT NULL UNIQUE,

                direction INTEGER NOT NULL DEFAULT 1,

                confidence REAL NOT NULL DEFAULT 0.0,

                active INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (site_id)
                    REFERENCES sites(id)
            )
            """
        )

        # ================================================
        # SITE SETTINGS
        # ================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS site_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                site_id INTEGER NOT NULL UNIQUE,

                aquarium_name TEXT,

                max_fishes INTEGER NOT NULL DEFAULT 300,

                fish_speed REAL NOT NULL DEFAULT 1.0,

                active INTEGER NOT NULL DEFAULT 1,

                FOREIGN KEY (site_id)
                    REFERENCES sites(id)
            )
            """
        )

        # ================================================
        # INDEXES
        # ================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_fishes_site_id
            ON fishes(site_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_users_site_id
            ON users(site_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_devices_site_id
            ON devices(site_id)
            """
        )

        # ================================================
        # INITIAL SITE
        # ================================================

        connection.execute(
            """
            INSERT OR IGNORE INTO sites (
                name,
                location,
                code,
                active
            )
            VALUES (?, ?, ?, 1)
            """,
            (
                "Основная площадка",
                "Astana",
                "ASTANA-MAIN",
            ),
        )

        # ================================================
        # INITIAL DEVICE
        # ================================================

        site = connection.execute(
            """
            SELECT id
            FROM sites
            WHERE code = ?
            """,
            ("ASTANA-MAIN",),
        ).fetchone()

        if site is not None:

            connection.execute(
                """
                INSERT OR IGNORE INTO devices (
                    site_id,
                    device_code,
                    name,
                    active
                )
                VALUES (?, ?, ?, 1)
                """,
                (
                    site["id"],
                    "ASTANA-SCREEN-001",
                    "Основной экран",
                ),
            )

        # ================================================
        # SAVE
        # ================================================

        connection.commit()

    finally:
        connection.close()