import cv2
import numpy as np


def normalize_lighting(
    image: np.ndarray
) -> np.ndarray:

    if image is None or image.size == 0:
        raise ValueError(
            "Изображение пустое."
        )

    image_float = image.astype(
        np.float32
    )

    # ==========================================
    # 1. ОЦЕНИВАЕМ ПЛАВНЫЙ ФОН
    # ==========================================

    background = cv2.GaussianBlur(
        image_float,
        (0, 0),
        sigmaX=35,
        sigmaY=35
    )

    background[
        background < 1
    ] = 1


    # ==========================================
    # 2. КОРРЕКЦИЯ ОСВЕЩЕНИЯ
    # ==========================================

    corrected = (
        image_float /
        background
    )


    # ==========================================
    # 3. НОРМАЛИЗУЕМ К СРЕДНЕМУ УРОВНЮ
    # ==========================================

    target = np.median(
        background.reshape(
            -1,
            3
        ),
        axis=0
    )

    corrected = (
        corrected *
        target
    )


    # ==========================================
    # 4. ОГРАНИЧИВАЕМ ЗНАЧЕНИЯ
    # ==========================================

    corrected = np.clip(
        corrected,
        0,
        255
    ).astype(
        np.uint8
    )

    return corrected