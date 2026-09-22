from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.upload import router as upload_router
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.device import router as device_router
from app.routes.preview import router as preview_router
from app.websocket_manager import manager
from app.device_config import get_device_code
from app.device_service import get_device_by_code
from app.fish_service import get_fishes_by_site
from app.database import init_database
# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent


# Создаём приложение FastAPI
app = FastAPI(
    title="Живой аквариум",
    description="Интерактивная инсталляция с детскими рисунками",
    version="0.1.0",
)
init_database()

# Подключаем API загрузки изображений
app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(device_router)
app.include_router(preview_router)
# ==================================================
# WEBSOCKET БОЛЬШОГО ЭКРАНА
# ==================================================

@app.websocket("/ws/screen")
async def screen_websocket(websocket: WebSocket):

    await manager.connect(websocket)

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(websocket)

    except Exception as error:

        print(
            "Ошибка WebSocket:",
            error
        )

        manager.disconnect(websocket)
        
# Подключаем папку static
# После этого браузер сможет загружать CSS, JavaScript и другие файлы.
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


# Тестовый API
@app.get("/")
async def root():
    return {
        "status": "ok",
        "project": "Живой аквариум",
        "message": "Сервер работает",
    }


# Страница большого экрана
@app.get("/screen")
async def screen():
    return FileResponse(
        BASE_DIR / "static" / "screen" / "index.html"
    )
@app.get("/login")
async def login_page():
    return FileResponse(
        BASE_DIR / "static" / "login" / "index.html"
    )

# Мобильная страница загрузки рисунка
@app.get("/upload")
async def upload():
    return FileResponse(
        BASE_DIR / "static" / "upload" / "index.html"
    )

# Административная панель
@app.get("/admin")
async def admin():
    return FileResponse(
        BASE_DIR / "static" / "admin" / "index.html"
    )

# Выдача обработанной рыбки
@app.get("/fish/{filename}")
async def get_fish(filename: str):

    fish_path = (
        BASE_DIR
        / "storage"
        / "fish"
        / filename
    )

    print("BASE_DIR:", BASE_DIR)
    print("FISH PATH:", fish_path)
    print("EXISTS:", fish_path.exists())

    if not fish_path.exists():
        return {
            "status": "error",
            "message": "Рыбка не найдена.",
            "path": str(fish_path),
        }

    return FileResponse(
        fish_path,
        media_type="image/png"
    )

# ==================================================
# РЫБКИ ТЕКУЩЕЙ ПЛОЩАДКИ
# ==================================================

@app.get("/api/fish")
async def get_all_fish():

    # Получаем код текущего устройства
    device_code = get_device_code()

    # Находим устройство
    device = get_device_by_code(
        device_code
    )

    if device is None:
        return {
            "status": "error",
            "message": "Устройство не зарегистрировано.",
            "count": 0,
            "fishes": [],
        }

    # Проверяем активность устройства
    if device["active"] != 1:
        return {
            "status": "error",
            "message": "Устройство отключено.",
            "count": 0,
            "fishes": [],
        }

    # Получаем площадку устройства
    site_id = device["site_id"]

    # Получаем рыбок только этой площадки
    fishes = get_fishes_by_site(
        site_id
    )

    result = []

    for fish in fishes:

        result.append({
            "id": fish["id"],
            "filename": fish["filename"],
            "url": f"/fish/{fish['filename']}",
            "direction": fish["direction"],
            "confidence": fish["confidence"],
        })

    return {
        "status": "ok",
        "site_id": site_id,
        "count": len(result),
        "fishes": result,
    }