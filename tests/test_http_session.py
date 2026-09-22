import http.client
import json


HOST = "127.0.0.1"
PORT = 8000


def main():
    print()
    print("=" * 60)
    print("ТЕСТ HTTP-СЕССИИ")
    print("=" * 60)

    # --------------------------------------------------
    # 1. LOGIN
    # --------------------------------------------------

    print()
    print("1. Авторизация")

    connection = http.client.HTTPConnection(
        HOST,
        PORT,
    )

    login_data = json.dumps({
        "username": "admin_astana",
        "password": "AdminPassword123!",
    })

    connection.request(
        "POST",
        "/api/auth/login",
        body=login_data,
        headers={
            "Content-Type": "application/json",
        },
    )

    response = connection.getresponse()

    login_body = response.read().decode(
        "utf-8"
    )

    print("HTTP:", response.status)

    if response.status != 200:
        print("Ошибка авторизации:")
        print(login_body)
        return

    print("Авторизация: OK")

    # --------------------------------------------------
    # 2. COOKIE
    # --------------------------------------------------

    print()
    print("2. Получение Cookie")

    set_cookie = response.getheader(
        "Set-Cookie"
    )

    if not set_cookie:
        print("Cookie: ОШИБКА — Cookie отсутствует")
        return

    print("Cookie получена: OK")

    cookie = set_cookie.split(
        ";",
        1
    )[0]

    print("Cookie:", cookie[:40] + "...")

    # --------------------------------------------------
    # 3. /ME
    # --------------------------------------------------

    print()
    print("3. Проверка /api/auth/me")

    connection.request(
        "GET",
        "/api/auth/me",
        headers={
            "Cookie": cookie,
        },
    )

    response = connection.getresponse()

    me_body = response.read().decode(
        "utf-8"
    )

    print("HTTP:", response.status)

    if response.status != 200:
        print("Ошибка:")
        print(me_body)
        return

    data = json.loads(me_body)

    print("Сессия: OK")
    print("Authenticated:", data["authenticated"])
    print("User ID:", data["user_id"])
    print("Site ID:", data["site_id"])
    print("Role:", data["role"])

    print()
    print("=" * 60)
    print("ТЕСТ HTTP-СЕССИИ ПРОЙДЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()