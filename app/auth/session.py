from itsdangerous import URLSafeTimedSerializer


SECRET_KEY = "CHANGE_THIS_SECRET_KEY"

SESSION_MAX_AGE = 60 * 60 * 8


serializer = URLSafeTimedSerializer(
    SECRET_KEY,
    salt="living-aquarium-session",
)


def create_session_token(
    user_id: int,
    site_id: int | None,
    role: str,
) -> str:

    data = {
        "user_id": user_id,
        "site_id": site_id,
        "role": role,
    }

    return serializer.dumps(data)


def read_session_token(
    token: str,
) -> dict | None:

    if not token:
        return None

    try:

        return serializer.loads(
            token,
            max_age=SESSION_MAX_AGE,
        )

    except Exception:
        return None