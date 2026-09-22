from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.image_processing.pipeline import process_drawing


router = APIRouter(
    prefix="/api/preview",
    tags=["preview"],
)


BASE_DIR = (
    Path(__file__).resolve().parent.parent.parent
)

PREVIEW_DIR = (
    BASE_DIR / "storage" / "previews"
)

PREVIEW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("")
async def preview_image(
    file: UploadFile = File(...)
):
    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Можно загрузить только изображение."
        )

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Фотография пустая."
        )

    max_size = 15 * 1024 * 1024

    if len(data) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Фотография слишком большая."
        )

    image_array = np.frombuffer(
        data,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Не удалось прочитать изображение."
        )

    preview_id = uuid4().hex

    preview_path = (
        PREVIEW_DIR
        / f"{preview_id}.png"
    )

    try:
        fish_image = process_drawing(image)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(
            "Ошибка preview:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Ошибка обработки изображения."
        )

    success = cv2.imwrite(
        str(preview_path),
        fish_image
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Не удалось сохранить preview."
        )

    return {
        "status": "ok",
        "preview_id": preview_id,
        "preview_url": (
            f"/api/preview/{preview_id}"
        )
    }


@router.get("/{preview_id}")
async def get_preview(
    preview_id: str
):
    preview_path = (
        PREVIEW_DIR
        / f"{preview_id}.png"
    )

    if not preview_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Preview не найден."
        )

    return FileResponse(
        preview_path,
        media_type="image/png"
    )