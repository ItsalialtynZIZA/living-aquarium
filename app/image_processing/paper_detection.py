import cv2
import numpy as np


def order_points(points: np.ndarray) -> np.ndarray:
    """
    Расставляет 4 точки в правильном порядке:

    0 — верхний левый
    1 — верхний правый
    2 — нижний правый
    3 — нижний левый
    """

    points = points.astype(np.float32)

    sums = points.sum(axis=1)

    top_left = points[np.argmin(sums)]
    bottom_right = points[np.argmax(sums)]

    differences = np.diff(points, axis=1).reshape(-1)

    top_right = points[np.argmin(differences)]
    bottom_left = points[np.argmax(differences)]

    return np.array(
        [
            top_left,
            top_right,
            bottom_right,
            bottom_left,
        ],
        dtype=np.float32,
    )


def is_valid_paper_quad(
    approx: np.ndarray,
    small_width: int,
    small_height: int,
) -> bool:
    """
    Проверяет, является ли найденный контур
    подходящим четырёхугольником листа.
    """

    # Должно быть ровно 4 угла
    if len(approx) != 4:
        return False

    # Контур должен быть выпуклым
    if not cv2.isContourConvex(approx):
        return False

    points = approx.reshape(4, 2)

    # Не принимаем границу фотографии
    # за лист бумаги.
    margin = 10

    if (
        np.any(points[:, 0] <= margin)
        or np.any(points[:, 1] <= margin)
        or np.any(points[:, 0] >= small_width - margin)
        or np.any(points[:, 1] >= small_height - margin)
    ):
        return False

    return True


def detect_paper(image: np.ndarray):
    """
    Ищет лист бумаги на фотографии.

    Используем два подхода:

    1. Canny + контуры.
    2. Адаптивный threshold + контуры.

    Возвращает 4 угла листа
    или None, если лист не найден.
    """

    # ==============================================
    # ПРОВЕРКА ИЗОБРАЖЕНИЯ
    # ==============================================

    if image is None or image.size == 0:
        return None

    height, width = image.shape[:2]

    # ==============================================
    # УМЕНЬШАЕМ ИЗОБРАЖЕНИЕ
    # ==============================================

    max_dimension = 1200

    scale = min(
        1.0,
        max_dimension / max(height, width)
    )

    if scale < 1.0:

        small = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    else:

        small = image.copy()

    small_height, small_width = small.shape[:2]

    small_area = small_height * small_width

    # ==============================================
    # GRAYSCALE
    # ==============================================

    gray = cv2.cvtColor(
        small,
        cv2.COLOR_BGR2GRAY
    )

    # ==============================================
    # BLUR
    # ==============================================

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    # ==============================================
    # СПОСОБ №1
    # CANNY
    # ==============================================

    edges = cv2.Canny(
        blurred,
        30,
        120
    )

    # Соединяем разорванные края
    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    # ==============================================
    # КОНТУРЫ
    # ==============================================

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    # ==============================================
    # ПРОВЕРКА КОНТУРОВ
    # ==============================================

    for contour in contours[:50]:

        area = cv2.contourArea(contour)

        # Лист должен занимать
        # минимум 10% фотографии
        if area < small_area * 0.10:
            continue

        perimeter = cv2.arcLength(
            contour,
            True
        )

        approx = cv2.approxPolyDP(
            contour,
            0.025 * perimeter,
            True
        )

        # Проверяем четырёхугольник
        if not is_valid_paper_quad(
            approx,
            small_width,
            small_height
        ):
            continue

        points = approx.reshape(4, 2)

        # Возвращаем координаты
        # к оригинальному размеру
        if scale < 1.0:
            points = points / scale

        return order_points(points)

    # ==============================================
    # СПОСОБ №2
    # ADAPTIVE THRESHOLD
    # ==============================================

    threshold = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        51,
        10
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    # ==============================================
    # КОНТУРЫ ПОРОГОВОЙ МАСКИ
    # ==============================================

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    # ==============================================
    # ПРОВЕРКА КОНТУРОВ
    # ==============================================

    for contour in contours[:50]:

        area = cv2.contourArea(contour)

        # Здесь немного выше порог
        if area < small_area * 0.15:
            continue

        perimeter = cv2.arcLength(
            contour,
            True
        )

        approx = cv2.approxPolyDP(
            contour,
            0.025 * perimeter,
            True
        )

        # Проверяем четырёхугольник
        if not is_valid_paper_quad(
            approx,
            small_width,
            small_height
        ):
            continue

        points = approx.reshape(4, 2)

        # Возвращаем координаты
        # к оригинальному размеру
        if scale < 1.0:
            points = points / scale

        return order_points(points)

    # ==============================================
    # ЛИСТ НЕ НАЙДЕН
    # ==============================================

    return None