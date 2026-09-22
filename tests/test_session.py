import sys
from pathlib import Path


PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR),
)


from app.auth.session import (
    create_session_token,
    read_session_token,
)


def main():

    print()
    print("=" * 60)
    print("ТЕСТ СЕССИИ АВТОРИЗАЦИИ")
    print("=" * 60)

    user_id = 1
    site_id = 1
    role = "site_admin"

    token = create_session_token(
        user_id=user_id,
        site_id=site_id,
        role=role,
    )

    print()
    print("Сессионный токен создан:")
    print(token)

    session = read_session_token(token)

    print()
    print("Данные сессии:")

    print("User ID:", session["user_id"])
    print("Site ID:", session["site_id"])
    print("Role:", session["role"])

    print()
    print("Проверка данных:")

    if session["user_id"] == user_id:
        print("User ID: OK")
    else:
        print("User ID: ОШИБКА")

    if session["site_id"] == site_id:
        print("Site ID: OK")
    else:
        print("Site ID: ОШИБКА")

    if session["role"] == role:
        print("Role: OK")
    else:
        print("Role: ОШИБКА")

    print()
    print("Проверка поддельного токена:")

    fake_session = read_session_token(
        token + "fake"
    )

    if fake_session is None:
        print("Поддельный токен отклонён: OK")
    else:
        print("ОШИБКА: поддельный токен принят")

    print()
    print("=" * 60)
    print("ТЕСТ СЕССИИ ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()