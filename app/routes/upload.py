from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from app.image_processing.pipeline import (
    process_drawing,
)

from app.websocket_manager import manager
from app.device_config import get_device_code
from app.device_service import get_device_by_code
from app.fish_service import create_fish

router = APIRouter()

from app.image_processing.fish_orientation import (
    detect_fish_orientation,
)

BASE_DIR = (
    Path(__file__).resolve().parent.parent.parent
)

ORIGINALS_DIR = (
    BASE_DIR / "storage" / "originals"
)

FISH_DIR = (
    BASE_DIR / "storage" / "fish"
)

DEBUG_DIR = (
    BASE_DIR / "storage" / "debug"
)


ORIGINALS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FISH_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DEBUG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("/api/upload")
async def upload_image(
    file: UploadFile = File(...)
):

    # ---------------------------------------------------------
    # Определяем площадку текущего устройства
    # ---------------------------------------------------------

    device_code = get_device_code()

    device = get_device_by_code(
        device_code
    )

    if device is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "Устройство не зарегистрировано."
            )
        )

    if device["active"] != 1:
        raise HTTPException(
            status_code=403,
            detail=(
                "Устройство отключено."
            )
        )

    site_id = device["site_id"]

    print(
        "Рисунок загружается на площадку:",
        site_id
    )

    # ---------------------------------------------------------
    # 1. Проверяем тип файла
    # ---------------------------------------------------------

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Можно загрузить только изображение."
            )
        )

    extension = (
        Path(
            file.filename or ""
        ).suffix.lower()
    )

    if extension not in [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]:
        extension = ".jpg"

    # ---------------------------------------------------------
    # 2. Читаем файл
    # ---------------------------------------------------------

    data = await file.read()

    max_size = 15 * 1024 * 1024

    if len(data) > max_size:
        raise HTTPException(
            status_code=400,
            detail=(
                "Фотография слишком большая."
            )
        )

    if len(data) == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Фотография пустая."
            )
        )

    # ---------------------------------------------------------
    # 3. Создаём ID
    # ---------------------------------------------------------

    drawing_id = uuid4().hex

    original_filename = (
        f"{drawing_id}{extension}"
    )

    original_path = (
        ORIGINALS_DIR
        / original_filename
    )

    # ---------------------------------------------------------
    # 4. Сохраняем оригинал
    # ---------------------------------------------------------

    original_path.write_bytes(
        data
    )

    # ---------------------------------------------------------
    # 5. Открываем изображение OpenCV
    # ---------------------------------------------------------

    image_array = np.frombuffer(
        data,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        original_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Не удалось прочитать изображение."
            )
        )

    # ---------------------------------------------------------
    # 6. Debug-папка конкретного рисунка
    # ---------------------------------------------------------

    drawing_debug_dir = (
        DEBUG_DIR / drawing_id
    )

    # ---------------------------------------------------------
    # 7. Запускаем OpenCV Pipeline
    # ---------------------------------------------------------

    try:

        fish_image = process_drawing(
            image,
            debug_dir=drawing_debug_dir
        )

        orientation = detect_fish_orientation(
            fish_image
        )

        print(
            "Ориентация рыбки:",
            orientation
        )

    except ValueError as error:

        original_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            "Ошибка обработки изображения:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Произошла ошибка "
                "при обработке рисунка."
            )
        )

    # ---------------------------------------------------------
    # 8. Сохраняем готовую рыбку
    # ---------------------------------------------------------

    fish_filename = (
        f"{drawing_id}.png"
    )

    fish_path = (
        FISH_DIR / fish_filename
    )

    success = cv2.imwrite(
        str(fish_path),
        fish_image
    )

    if not success:

        raise HTTPException(
            status_code=500,
            detail=(
                "Не удалось сохранить "
                "обработанный рисунок."
            )
        )

    # ---------------------------------------------------------
    # 9. Сохраняем рыбку в базе данных
    # ---------------------------------------------------------

    try:

        fish_id = create_fish(
            site_id=site_id,
            filename=fish_filename,
            direction=orientation["direction"],
            confidence=orientation["confidence"],
        )

        print(
            "Рыбка сохранена в БД:",
            fish_id
        )

    except ValueError as error:

        fish_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            "Ошибка сохранения рыбки в БД:",
            error
        )

        fish_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Не удалось сохранить "
                "рыбку в базе данных."
            )
        )
    # ---------------------------------------------------------
    # 10. Сообщаем большому экрану о новой рыбке
    # ---------------------------------------------------------

    await manager.broadcast(
        {
            "type": "new_fish",
            "fish_id": fish_id,
            "filename": fish_filename,
            "url": f"/fish/{fish_filename}",
            "direction": orientation["direction"],
            "confidence": orientation["confidence"],
            "site_id": site_id,
        }
    )


    # ---------------------------------------------------------
    # 11. Ответ
    # ---------------------------------------------------------

    return {
        "status": "ok",
        "message": "Рисунок обработан.",
        "drawing_id": drawing_id,
        "original": original_filename,
        "fish": fish_filename,
        "fish_url": f"/fish/{fish_filename}",
        "direction": orientation["direction"],
        "confidence": orientation["confidence"],
    }