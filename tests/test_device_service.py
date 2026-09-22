import sys
from pathlib import Path

PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR)
)

from app.database import (
    init_database,
    get_connection,
)

from app.device_service import (
    create_device,
    get_device_by_code,
    update_device_last_seen,
    register_device,
)


def test_create_device():

    print()
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ УСТРОЙСТВА")
    print("=" * 60)

    init_database()

    device_id = create_device(
        site_id=1,
        device_code="ASTANA-SCREEN-004",
        name="Тестовый экран",
    )

    print()
    print("Устройство создано: OK")
    print("ID:", device_id)

    connection = get_connection()

    try:

        device = connection.execute(
            """
            SELECT
                id,
                site_id,
                device_code,
                name,
                active
            FROM devices
            WHERE id = ?
            """,
            (device_id,),
        ).fetchone()

        if device is None:
            print("ОШИБКА: устройство не найдено")
            return

        print()
        print("Данные устройства:")
        print("ID:", device["id"])
        print("Site ID:", device["site_id"])
        print("Код:", device["device_code"])
        print("Название:", device["name"])
        print("Активно:", device["active"])

    finally:
        connection.close()

    print()
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ УСТРОЙСТВА ПРОЙДЕН")
    print("=" * 60)


def test_get_device_by_code():

    print()
    print("=" * 60)
    print("ТЕСТ ПОЛУЧЕНИЯ УСТРОЙСТВА")
    print("=" * 60)

    print()
    print("1. Существующее устройство")

    device = get_device_by_code(
        "ASTANA-SCREEN-001"
    )

    if device is None:
        print("ОШИБКА: устройство не найдено")
        return

    print("Устройство найдено: OK")
    print("ID:", device["id"])
    print("Site ID:", device["site_id"])
    print("Код:", device["device_code"])
    print("Название:", device["name"])
    print("Активно:", device["active"])

    print()
    print("2. Несуществующее устройство")

    device = get_device_by_code(
        "NOT-EXIST-999"
    )

    if device is None:
        print("Несуществующее устройство отклонено: OK")
    else:
        print("ОШИБКА: несуществующее устройство найдено")

    print()
    print("=" * 60)
    print("ТЕСТ ПОЛУЧЕНИЯ УСТРОЙСТВА ПРОЙДЕН")
    print("=" * 60)


def test_update_device_last_seen():

    print()
    print("=" * 60)
    print("ТЕСТ ОБНОВЛЕНИЯ LAST_SEEN")
    print("=" * 60)

    device_code = "ASTANA-SCREEN-001"

    print()
    print("Устройство:", device_code)

    result = update_device_last_seen(
        device_code
    )

    if not result:
        print("ОШИБКА: устройство не найдено или отключено")
        return

    print("LAST_SEEN обновлён: OK")

    device = get_device_by_code(
        device_code
    )

    if device is None:
        print("ОШИБКА: устройство не найдено после обновления")
        return

    print(
        "Последнее подключение:",
        device["last_seen"]
    )

    print()
    print("=" * 60)
    print("ТЕСТ LAST_SEEN ПРОЙДЕН")
    print("=" * 60)


def test_register_device():

    print()
    print("=" * 60)
    print("ТЕСТ РЕГИСТРАЦИИ УСТРОЙСТВА")
    print("=" * 60)

    device_code = "ASTANA-SCREEN-001"

    print()
    print(
        "Регистрация устройства:",
        device_code
    )

    device = register_device(
        device_code
    )

    if device is None:
        print("ОШИБКА: устройство не зарегистрировано")
        return

    print("Устройство зарегистрировано: OK")
    print("ID:", device["id"])
    print("Site ID:", device["site_id"])
    print("Код:", device["device_code"])
    print("Название:", device["name"])
    print("Активно:", device["active"])
    print(
        "Последнее подключение:",
        device["last_seen"]
    )

    print()
    print("=" * 60)
    print("ТЕСТ РЕГИСТРАЦИИ УСТРОЙСТВА ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":

    test_create_device()
    test_get_device_by_code()
    test_update_device_last_seen()
    test_register_device()