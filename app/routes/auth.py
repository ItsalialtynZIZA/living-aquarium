from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from app.auth.service import authenticate_user
from app.auth.dependencies import require_site_admin


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    data: LoginRequest,
    response: Response,
):
    result = authenticate_user(
        username=data.username,
        password=data.password,
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль.",
        )

    response.set_cookie(
        key="living_aquarium_session",
        value=result["token"],
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 8,
    )

    return {
        "status": "ok",
        "user_id": result["user_id"],
        "username": result["username"],
        "role": result["role"],
        "site_id": result["site_id"],
    }


class AdminLoginRequest(BaseModel):
    password: str


@router.post("/admin-login")
async def admin_login(
    data: AdminLoginRequest,
    response: Response,
):
    if data.password != "0913":
        raise HTTPException(
            status_code=401,
            detail="Неверный пароль.",
        )

    from app.database import get_connection
    from app.auth.session import create_session_token

    connection = get_connection()

    try:
        user = connection.execute(
            """
            SELECT
                id,
                username,
                role,
                site_id,
                active
            FROM users
            WHERE role = 'site_admin'
            AND active = 1
            ORDER BY id ASC
            LIMIT 1
            """
        ).fetchone()
    finally:
        connection.close()

    if user is None:
        raise HTTPException(
            status_code=500,
            detail="Активный администратор площадки не найден.",
        )

    token = create_session_token(
        user_id=user["id"],
        site_id=user["site_id"],
        role=user["role"],
    )

    response.set_cookie(
        key="living_aquarium_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 8,
    )

    return {
        "status": "ok",
        "username": user["username"],
        "role": user["role"],
        "site_id": user["site_id"],
    }


@router.get("/me")
async def get_current_user(
    request: Request,
):
    token = request.cookies.get(
        "living_aquarium_session"
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не авторизован.",
        )

    from app.auth.session import read_session_token

    session = read_session_token(token)

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Сессия недействительна или истекла.",
        )

    return {
        "authenticated": True,
        "user_id": session["user_id"],
        "site_id": session["site_id"],
        "role": session["role"],
    }


@router.get("/protected")
async def protected(
    user: dict = Depends(require_site_admin),
):
    return {
        "status": "ok",
        "message": "Доступ разрешён.",
        "user_id": user["user_id"],
        "site_id": user["site_id"],
        "role": user["role"],
    }


@router.post("/logout")
async def logout(
    response: Response,
):
    response.delete_cookie(
        key="living_aquarium_session"
    )

    return {
        "status": "ok",
        "message": "Выход выполнен.",
    }