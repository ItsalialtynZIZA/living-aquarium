import cv2
import numpy as np


def create_rgba(
    image: np.ndarray,
    mask: np.ndarray
) -> np.ndarray:
    """
    Создаёт RGBA-изображение рисунка
    с прозрачным фоном.

    image:
        Цветное изображение после нормализации.

    mask:
        Очищенная бинарная маска рисунка.

    return:
        Изображение BGRA.
    """

    if image is None or image.size == 0:
        raise ValueError("Изображение пустое.")

    if mask is None or mask.size == 0:
        raise ValueError("Маска пустая.")

    if image.shape[:2] != mask.shape[:2]:
        raise ValueError(
            "Размер изображения и маски не совпадает."
        )

    # ---------------------------------------------------------
    # 1. Сглаживаем края маски
    # ---------------------------------------------------------

    alpha = cv2.GaussianBlur(
        mask,
        (5, 5),
        sigmaX=0
    )

    # ---------------------------------------------------------
    # 2. Переводим BGR -> BGRA
    # ---------------------------------------------------------

    rgba = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2BGRA
    )

    # ---------------------------------------------------------
    # 3. Маску используем как Alpha-канал
    # ---------------------------------------------------------

    rgba[:, :, 3] = alpha

    return rgba