import sys
from pathlib import Path


PROJECT_DIR = Path(
    r"C:\living-aquarium"
)

sys.path.insert(
    0,
    str(PROJECT_DIR),
)


from app.database import get_connection
from app.auth.password import verify_password
from app.user_service import create_site_admin


def main():

    print()
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ SITE ADMIN")
    print("=" * 60)

    username = "admin_astana"
    password = "AdminPassword123!"
    site_id = 1

    user_id = create_site_admin(
        username=username,
        password=password,
        site_id=site_id,
    )

    print()
    print("Администратор создан.")
    print("ID:", user_id)
    print("Логин:", username)
    print("Роль: site_admin")
    print("Site ID:", site_id)

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
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        print()
        print("Данные пользователя:")

        print("ID:", user["id"])
        print("Логин:", user["username"])
        print("Роль:", user["role"])
        print("Site ID:", user["site_id"])
        print("Активен:", user["active"])

        print()
        print("Проверка пароля:")

        password_ok = verify_password(
            password,
            user["password_hash"],
        )

        wrong_password_ok = verify_password(
            "WrongPassword123!",
            user["password_hash"],
        )

        if password_ok:
            print("Правильный пароль: OK")
        else:
            print("Правильный пароль: ОШИБКА")

        if not wrong_password_ok:
            print("Неправильный пароль: OK")
        else:
            print("Неправильный пароль: ОШИБКА")

        print()
        print("Проверка хеша:")

        if user["password_hash"].startswith("$argon2"):
            print("Argon2: OK")
        else:
            print("Argon2: ОШИБКА")

    finally:
        connection.close()

    print()
    print("=" * 60)
    print("ТЕСТ SITE ADMIN ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()