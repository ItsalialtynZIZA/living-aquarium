import sys
from pathlib import Path


PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR),
)


from app.database import init_database, get_connection
from app.site_service import create_site


def main():

    print()
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ ПЛОЩАДКИ")
    print("=" * 60)

    init_database()

    site_id = create_site(
        name="Главная площадка",
        location="Astana",
        code="ASTANA-001",
    )

    print()
    print("Площадка создана.")
    print("ID:", site_id)

    connection = get_connection()

    try:

        site = connection.execute(
            """
            SELECT
                id,
                name,
                location,
                code,
                active
            FROM sites
            WHERE id = ?
            """,
            (site_id,),
        ).fetchone()

        print()
        print("Данные площадки:")

        print("ID:", site["id"])
        print("Название:", site["name"])
        print("Местоположение:", site["location"])
        print("Код:", site["code"])
        print("Активна:", site["active"])

    finally:
        connection.close()

    print()
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ ПЛОЩАДКИ ПРОЙДЕН")
    print("=" * 60)

def test_get_site():
    from app.site_service import get_site_by_id

    print()
    print("=" * 60)
    print("ТЕСТ ПОЛУЧЕНИЯ ПЛОЩАДКИ")
    print("=" * 60)

    print()
    print("1. Существующая площадка")

    site = get_site_by_id(1)

    if site is None:
        print("ОШИБКА: площадка не найдена")
        return

    print("Площадка найдена: OK")
    print("ID:", site["id"])
    print("Название:", site["name"])
    print("Местоположение:", site["location"])
    print("Код:", site["code"])
    print("Активна:", site["active"])

    print()
    print("2. Несуществующая площадка")

    site = get_site_by_id(999999)

    if site is None:
        print("Площадка не найдена: OK")
    else:
        print("ОШИБКА: несуществующая площадка найдена")

    print()
    print("=" * 60)
    print("ТЕСТ ПОЛУЧЕНИЯ ПЛОЩАДКИ ПРОЙДЕН")
    print("=" * 60)
def test_get_active_site():
    from app.site_service import get_active_site_by_id

    print()
    print("=" * 60)
    print("ТЕСТ АКТИВНОЙ ПЛОЩАДКИ")
    print("=" * 60)

    print()
    print("1. Активная площадка")

    site = get_active_site_by_id(1)

    if site is None:
        print("ОШИБКА: активная площадка не найдена")
        return

    print("Активная площадка найдена: OK")
    print("ID:", site["id"])
    print("Название:", site["name"])
    print("Активна:", site["active"])

    print()
    print("2. Несуществующая площадка")

    site = get_active_site_by_id(999999)

    if site is None:
        print("Несуществующая площадка отклонена: OK")
    else:
        print("ОШИБКА: несуществующая площадка найдена")

    print()
    print("=" * 60)
    print("ТЕСТ АКТИВНОЙ ПЛОЩАДКИ ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":
    test_get_site()
    test_get_active_site()