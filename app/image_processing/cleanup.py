import cv2
import numpy as np


def clean_mask(
    mask: np.ndarray
) -> np.ndarray:
    """
    Мягкая очистка маски рисунка.

    Сохраняет:
    - внутренние линии;
    - глаза;
    - рот;
    - мелкие детали;
    - тонкие элементы рисунка.

    Убирает:
    - отдельный мелкий шум;
    - небольшие разрывы линий.
    """

    if mask is None or mask.size == 0:
        raise ValueError(
            "Маска пустая."
        )

    result = mask.copy()


    # =========================================================
    # 1. ОЧЕНЬ МЯГКОЕ УДАЛЕНИЕ ШУМА
    # =========================================================

    kernel_open = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (2, 2)
    )

    result = cv2.morphologyEx(
        result,
        cv2.MORPH_OPEN,
        kernel_open
    )


    # =========================================================
    # 2. СОХРАНЯЕМ И СОЕДИНЯЕМ ДЕТАЛИ
    # =========================================================

    kernel_close = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    result = cv2.morphologyEx(
        result,
        cv2.MORPH_CLOSE,
        kernel_close
    )


    # =========================================================
    # 3. ЛЁГКОЕ ЗАПОЛНЕНИЕ МЕЛКИХ ПРОБЕЛОВ
    # =========================================================

    result = cv2.GaussianBlur(
        result,
        (3, 3),
        0
    )

    result = np.where(
        result > 80,
        255,
        0
    ).astype(
        np.uint8
    )


    return result