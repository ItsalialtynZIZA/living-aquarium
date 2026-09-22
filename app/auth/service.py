from app.auth.password import verify_password
from app.auth.session import create_session_token
from app.database import get_connection


def authenticate_user(
    username: str,
    password: str,
) -> dict | None:

    if not username.strip():
        return None

    if not password:
        return None

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                role,
                site_id,
                active
            FROM users
            WHERE username = ?
            """,
            (username.strip(),),
        ).fetchone()

    finally:
        connection.close()

    if user is None:
        return None

    if user["active"] != 1:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    token = create_session_token(
        user_id=user["id"],
        site_id=user["site_id"],
        role=user["role"],
    )

    return {
        "token": token,
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "site_id": user["site_id"],
    }