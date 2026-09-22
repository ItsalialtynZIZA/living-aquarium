import cv2
import numpy as np


def four_point_transform(
    image: np.ndarray,
    points: np.ndarray
) -> np.ndarray:
    """
    Выравнивает лист бумаги по четырём найденным углам.

    points должны идти в порядке:

    0 — верхний левый
    1 — верхний правый
    2 — нижний правый
    3 — нижний левый
    """

    # ==============================================
    # ПРОВЕРКА
    # ==============================================

    if image is None or image.size == 0:
        raise ValueError("Изображение пустое.")

    if points is None or len(points) != 4:
        raise ValueError(
            "Для перспективного преобразования "
            "нужно ровно 4 точки."
        )

    points = points.astype(np.float32)

    # ==============================================
    # РАЗБИРАЕМ ЧЕТЫРЕ УГЛА
    # ==============================================

    top_left = points[0]
    top_right = points[1]
    bottom_right = points[2]
    bottom_left = points[3]

    # ==============================================
    # ВЫЧИСЛЯЕМ ШИРИНУ
    # ==============================================

    width_top = np.linalg.norm(
        top_right - top_left
    )

    width_bottom = np.linalg.norm(
        bottom_right - bottom_left
    )

    max_width = int(
        max(width_top, width_bottom)
    )

    # ==============================================
    # ВЫЧИСЛЯЕМ ВЫСОТУ
    # ==============================================

    height_left = np.linalg.norm(
        bottom_left - top_left
    )

    height_right = np.linalg.norm(
        bottom_right - top_right
    )

    max_height = int(
        max(height_left, height_right)
    )

    # ==============================================
    # ЗАЩИТА ОТ НЕКОРРЕКТНЫХ РАЗМЕРОВ
    # ==============================================

    if max_width < 10 or max_height < 10:
        raise ValueError(
            "Слишком маленький или некорректный лист."
        )

    # ==============================================
    # ЦЕЛЕВЫЕ ТОЧКИ
    # ==============================================

    destination = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype=np.float32
    )

    # ==============================================
    # ПЕРСПЕКТИВНАЯ МАТРИЦА
    # ==============================================

    matrix = cv2.getPerspectiveTransform(
        points,
        destination
    )

    # ==============================================
    # ПЕРСПЕКТИВНОЕ ПРЕОБРАЗОВАНИЕ
    # ==============================================

    warped = cv2.warpPerspective(
        image,
        matrix,
        (max_width, max_height)
    )

    return warped