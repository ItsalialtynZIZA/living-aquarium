from app.database import get_connection


def create_fish(
    site_id: int,
    filename: str,
    direction: int,
    confidence: float,
) -> int:

    if site_id <= 0:
        raise ValueError(
            "Некорректный ID площадки."
        )

    if not filename.strip():
        raise ValueError(
            "Имя файла рыбки не может быть пустым."
        )

    if direction not in (-1, 1):
        raise ValueError(
            "Направление рыбки должно быть -1 или 1."
        )

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            "Confidence должен быть от 0 до 1."
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


        settings = connection.execute(
            """
            SELECT max_fishes
            FROM site_settings
            WHERE site_id = ?
            """,
            (site_id,),
        ).fetchone()

        if settings is None:
            raise ValueError(
                "Настройки площадки не найдены."
            )

        active_fishes = connection.execute(
            """
            SELECT COUNT(*)
            FROM fishes
            WHERE site_id = ?
            AND active = 1
            """,
            (site_id,),
        ).fetchone()[0]

        if active_fishes >= settings["max_fishes"]:
            raise ValueError(
                "На этой площадке достигнут "
                "максимальный лимит рыбок."
            )

        cursor = connection.execute(
            """
            INSERT INTO fishes (
                site_id,
                filename,
                direction,
                confidence
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                site_id,
                filename.strip(),
                direction,
                confidence,
            ),
        )

        fish_id = cursor.lastrowid

        connection.commit()

        return fish_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_fishes_by_site(
    site_id: int,
) -> list[dict]:

    if site_id <= 0:
        return []

    connection = get_connection()

    try:

        fishes = connection.execute(
            """
            SELECT
                id,
                site_id,
                filename,
                direction,
                confidence,
                active,
                created_at
            FROM fishes
            WHERE site_id = ?
            AND active = 1
            ORDER BY id ASC
            """,
            (site_id,),
        ).fetchall()

        return [
            dict(fish)
            for fish in fishes
        ]

    finally:
        connection.close()

def deactivate_fish(
    fish_id: int,
    site_id: int,
) -> bool:

    if fish_id <= 0:
        return False

    if site_id <= 0:
        return False

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            UPDATE fishes
            SET active = 0
            WHERE id = ?
            AND site_id = ?
            AND active = 1
            """,
            (
                fish_id,
                site_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()

def deactivate_all_fishes(
    site_id: int,
) -> list[int]:

    if site_id <= 0:
        return []

    connection = get_connection()

    try:

        fishes = connection.execute(
            """
            SELECT id
            FROM fishes
            WHERE site_id = ?
            AND active = 1
            ORDER BY id ASC
            """,
            (site_id,),
        ).fetchall()

        fish_ids = [
            fish["id"]
            for fish in fishes
        ]

        if not fish_ids:
            return []

        connection.execute(
            """
            UPDATE fishes
            SET active = 0
            WHERE site_id = ?
            AND active = 1
            """,
            (site_id,),
        )

        connection.commit()

        return fish_ids

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()