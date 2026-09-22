import sys
from pathlib import Path


PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR),
)


from app.auth.password import (
    hash_password,
    verify_password,
)


def main():

    password = "TestPassword123!"

    hashed = hash_password(password)

    print()
    print("=" * 60)
    print("ТЕСТ ХЕШИРОВАНИЯ ПАРОЛЯ")
    print("=" * 60)

    print()
    print("Исходный пароль:")
    print(password)

    print()
    print("Хеш:")
    print(hashed)

    print()
    print("Проверка правильного пароля:")

    if verify_password(password, hashed):
        print("OK")
    else:
        print("ОШИБКА")

    print()
    print("Проверка неправильного пароля:")

    if not verify_password(
        "WrongPassword123!",
        hashed,
    ):
        print("OK")
    else:
        print("ОШИБКА")

    print()
    print("=" * 60)
    print("ТЕСТ ПАРОЛЯ ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()