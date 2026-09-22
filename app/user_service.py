from app.auth.password import hash_password
from app.database import get_connection


def create_site_admin(
    username: str,
    password: str,
    site_id: int,
) -> int:

    if not username.strip():
        raise ValueError(
            "Логин не может быть пустым."
        )

    if not password:
        raise ValueError(
            "Пароль не может быть пустым."
        )

    if site_id <= 0:
        raise ValueError(
            "Некорректный ID площадки."
        )

    password_hash = hash_password(password)

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
            INSERT INTO users (
                username,
                password_hash,
                role,
                site_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username.strip(),
                password_hash,
                "site_admin",
                site_id,
            ),
        )

        user_id = cursor.lastrowid

        connection.commit()

        return user_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()