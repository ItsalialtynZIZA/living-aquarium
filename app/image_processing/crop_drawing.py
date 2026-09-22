import cv2
import numpy as np


def crop_drawing(
    image: np.ndarray,
    mask: np.ndarray,
    padding: int = 20
) -> np.ndarray:
    """
    Обрезает изображение вокруг рыбки.

    image:
        изображение A4.

    mask:
        маска рыбки:
        255 = рыбка
        0 = фон.

    padding:
        отступ вокруг рыбки.
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Изображение пустое."
        )

    if mask is None or mask.size == 0:
        raise ValueError(
            "Маска пустая."
        )

    if image.shape[:2] != mask.shape[:2]:
        raise ValueError(
            "Размер изображения и маски не совпадает."
        )

    if padding < 0:
        raise ValueError(
            "Padding не может быть отрицательным."
        )

    height, width = mask.shape[:2]

    # Убираем возможный шум непосредственно
    # у краёв листа.
    border = max(
        5,
        int(min(height, width) * 0.01)
    )

    clean_mask = mask.copy()

    clean_mask[:border, :] = 0
    clean_mask[height - border:, :] = 0
    clean_mask[:, :border] = 0
    clean_mask[:, width - border:] = 0

    # Ищем все пиксели рыбки.
    points = cv2.findNonZero(
        clean_mask
    )

    if points is None:
        raise ValueError(
            "Рисунок внутри A4 не найден."
        )

    # Получаем прямоугольник,
    # содержащий всю рыбку.
    x, y, w, h = cv2.boundingRect(
        points
    )

    # Добавляем отступ.
    x1 = max(
        0,
        x - padding
    )

    y1 = max(
        0,
        y - padding
    )

    x2 = min(
        width,
        x + w + padding
    )

    y2 = min(
        height,
        y + h + padding
    )

    if x2 <= x1 or y2 <= y1:
        raise ValueError(
            "Некорректная область обрезки рыбки."
        )

    # Обрезаем изображение.
    cropped = image[
        y1:y2,
        x1:x2
    ].copy()

    return cropped