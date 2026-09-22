import cv2
import numpy as np


def resize_rgba(
    rgba: np.ndarray,
    max_size: int = 1024
) -> np.ndarray:
    """
    Уменьшает RGBA/BGRA изображение,
    сохраняя пропорции.

    Если изображение уже меньше max_size,
    возвращает его без изменений.
    """

    if rgba is None or rgba.size == 0:
        raise ValueError(
            "RGBA-изображение пустое."
        )

    if rgba.ndim != 3:
        raise ValueError(
            "Ожидается RGBA/BGRA изображение."
        )

    if rgba.shape[2] != 4:
        raise ValueError(
            "Изображение должно содержать 4 канала."
        )

    if max_size < 64:
        raise ValueError(
            "max_size слишком маленький."
        )

    height, width = rgba.shape[:2]

    largest_side = max(
        width,
        height
    )

    if largest_side <= max_size:
        return rgba

    scale = (
        max_size /
        largest_side
    )

    new_width = max(
        1,
        int(width * scale)
    )

    new_height = max(
        1,
        int(height * scale)
    )

    resized = cv2.resize(
        rgba,
        (
            new_width,
            new_height
        ),
        interpolation=cv2.INTER_AREA
    )

    return resized