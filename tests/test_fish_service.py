import sys
from pathlib import Path


PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR),
)


from app.database import init_database
from app.fish_service import (
    create_fish,
    get_fishes_by_site,
)


def test_create_fish():

    print()
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ РЫБКИ")
    print("=" * 60)

    init_database()

    fish_id = create_fish(
        site_id=1,
        filename="test_fish_002.png",
        direction=1,
        confidence=0.45,
    )

    print()
    print("Рыбка создана: OK")
    print("ID:", fish_id)

    print()
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ РЫБКИ ПРОЙДЕН")
    print("=" * 60)


def test_get_fishes_by_site():

    print()
    print("=" * 60)
    print("ТЕСТ ПОЛУЧЕНИЯ РЫБОК ПЛОЩАДКИ")
    print("=" * 60)

    fishes = get_fishes_by_site(1)

    print()
    print("Количество рыбок:", len(fishes))

    if len(fishes) == 0:
        print("ОШИБКА: рыбки не найдены")
        return

    for fish in fishes:

        print()
        print("Рыбка:")
        print("ID:", fish["id"])
        print("Site ID:", fish["site_id"])
        print("Файл:", fish["filename"])
        print("Направление:", fish["direction"])
        print("Confidence:", fish["confidence"])
        print("Активна:", fish["active"])

    print()
    print("=" * 60)
    print("ТЕСТ ПОЛУЧЕНИЯ РЫБОК ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":
    test_create_fish()
    test_get_fishes_by_site()