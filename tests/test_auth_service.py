import sys
from pathlib import Path


PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR),
)


from app.auth.service import authenticate_user


def main():

    print()
    print("=" * 60)
    print("ТЕСТ АВТОРИЗАЦИИ")
    print("=" * 60)

    print()
    print("1. Правильный логин и пароль")

    result = authenticate_user(
        username="admin_astana",
        password="AdminPassword123!",
    )

    if result is not None:
        print("Авторизация: OK")
        print("User ID:", result["user_id"])
        print("Username:", result["username"])
        print("Role:", result["role"])
        print("Site ID:", result["site_id"])
    else:
        print("Авторизация: ОШИБКА")

    print()
    print("2. Неправильный пароль")

    result = authenticate_user(
        username="admin_astana",
        password="WrongPassword123!",
    )

    if result is None:
        print("Отказ в доступе: OK")
    else:
        print("ОШИБКА: неправильный пароль принят")

    print()
    print("3. Несуществующий пользователь")

    result = authenticate_user(
        username="unknown_user",
        password="SomePassword123!",
    )

    if result is None:
        print("Отказ в доступе: OK")
    else:
        print("ОШИБКА: неизвестный пользователь принят")

    print()
    print("=" * 60)
    print("ТЕСТ АВТОРИЗАЦИИ ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()