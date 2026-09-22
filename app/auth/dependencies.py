from fastapi import Cookie, Depends, HTTPException

from app.auth.session import read_session_token

from app.site_service import get_site_by_id


async def get_current_user(
    living_aquarium_session: str | None = Cookie(
        default=None
    ),
) -> dict:

    if not living_aquarium_session:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не авторизован.",
        )

    session = read_session_token(
        living_aquarium_session
    )

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Сессия недействительна или истекла.",
        )

    return session


async def require_site_admin(
    user: dict = Depends(get_current_user),
) -> dict:

    if user.get("role") != "site_admin":
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав.",
        )

    site_id = user.get("site_id")

    if site_id is None:
        raise HTTPException(
            status_code=403,
            detail="Площадка пользователя не определена.",
        )

    site = get_site_by_id(site_id)

    if site is None:
        raise HTTPException(
            status_code=403,
            detail="Площадка не найдена.",
        )

    if site["active"] != 1:
        raise HTTPException(
            status_code=403,
            detail="Площадка отключена.",
        )

    return user


async def require_super_admin(
    user: dict = Depends(get_current_user),
) -> dict:

    if user.get("role") != "super_admin":
        raise HTTPException(
            status_code=403,
            detail="Требуются права главного администратора.",
        )

    return user