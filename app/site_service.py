from app.database import get_connection


def create_site(
    name: str,
    location: str,
    code: str,
) -> int:

    if not name.strip():
        raise ValueError(
            "Название площадки не может быть пустым."
        )

    if not code.strip():
        raise ValueError(
            "Код площадки не может быть пустым."
        )

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            INSERT INTO sites (
                name,
                location,
                code
            )
            VALUES (?, ?, ?)
            """,
            (
                name.strip(),
                location.strip(),
                code.strip(),
            ),
        )

        site_id = cursor.lastrowid

        connection.commit()

        return site_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_site_by_id(
    site_id: int,
) -> dict | None:

    if site_id <= 0:
        return None

    connection = get_connection()

    try:
        site = connection.execute(
            """
            SELECT
                id,
                name,
                location,
                code,
                active,
                created_at
            FROM sites
            WHERE id = ?
            """,
            (site_id,),
        ).fetchone()

        if site is None:
            return None

        return dict(site)

    finally:
        connection.close()

def get_active_site_by_id(
    site_id: int,
) -> dict | None:

    site = get_site_by_id(site_id)

    if site is None:
        return None

    if site["active"] != 1:
        return None

    return site