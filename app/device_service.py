from app.database import get_connection


def create_device(
    site_id: int,
    device_code: str,
    name: str,
) -> int:

    if site_id <= 0:
        raise ValueError(
            "Некорректный ID площадки."
        )

    if not device_code.strip():
        raise ValueError(
            "Код устройства не может быть пустым."
        )

    if not name.strip():
        raise ValueError(
            "Название устройства не может быть пустым."
        )

    connection = get_connection()

    try:

        site = connection.execute(
            """
            SELECT id
            FROM sites
            WHERE id = ?
            AND active = 1
            """,
            (site_id,),
        ).fetchone()

        if site is None:
            raise ValueError(
                "Активная площадка не найдена."
            )

        cursor = connection.execute(
            """
            INSERT INTO devices (
                site_id,
                device_code,
                name
            )
            VALUES (?, ?, ?)
            """,
            (
                site_id,
                device_code.strip(),
                name.strip(),
            ),
        )

        device_id = cursor.lastrowid

        connection.commit()

        return device_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_device_by_code(
    device_code: str,
) -> dict | None:

    if not device_code.strip():
        return None

    connection = get_connection()

    try:

        device = connection.execute(
            """
            SELECT
                id,
                site_id,
                device_code,
                name,
                last_seen,
                active,
                created_at
            FROM devices
            WHERE device_code = ?
            """,
            (device_code.strip(),),
        ).fetchone()

        if device is None:
            return None

        return dict(device)

    finally:
        connection.close()

def update_device_last_seen(
    device_code: str,
) -> bool:

    if not device_code.strip():
        return False

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            UPDATE devices
            SET last_seen = CURRENT_TIMESTAMP
            WHERE device_code = ?
            AND active = 1
            """,
            (device_code.strip(),),
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def register_device(
    device_code: str,
) -> dict | None:

    if not device_code.strip():
        return None

    device = get_device_by_code(
        device_code
    )

    if device is None:
        return None

    if device["active"] != 1:
        return None

    update_device_last_seen(
        device_code
    )

    device["last_seen"] = (
        get_device_by_code(
            device_code
        )["last_seen"]
    )

    return device