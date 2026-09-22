import sys
from pathlib import Path


PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR),
)


from app.database import (
    init_database,
    get_connection,
    DATABASE_PATH,
)


EXPECTED_TABLES = [
    "sites",
    "users",
    "devices",
    "fishes",
    "site_settings",
]


def main():

    print()
    print("=" * 60)
    print("ТЕСТ MULTI-SITE SQLITE")
    print("ЖИВОЙ АКВАРИУМ")
    print("=" * 60)

    print()
    print("Инициализация базы...")

    init_database()

    print()
    print("База данных:")
    print(DATABASE_PATH)

    if not DATABASE_PATH.exists():
        print()
        print("ОШИБКА: база не создана.")
        return

    print()
    print("База создана: OK")

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        tables = [
            row["name"]
            for row in rows
        ]

        print()
        print("Найденные таблицы:")

        for table in tables:
            print(f"  ✓ {table}")

        print()
        print("Проверка необходимых таблиц:")

        all_ok = True

        for table in EXPECTED_TABLES:

            if table in tables:
                print(
                    f"  ✓ {table}: OK"
                )
            else:
                print(
                    f"  ✗ {table}: ОТСУТСТВУЕТ"
                )
                all_ok = False

        print()

        if all_ok:
            print("=" * 60)
            print("MULTI-SITE SQLITE ТЕСТ ПРОЙДЕН")
            print("=" * 60)
        else:
            print("=" * 60)
            print("ТЕСТ НЕ ПРОЙДЕН")
            print("=" * 60)

    finally:
        connection.close()


if __name__ == "__main__":
    main()