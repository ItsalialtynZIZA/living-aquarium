import cv2
import numpy as np


def _remove_border_components(mask: np.ndarray, border_size: int = 8) -> np.ndarray:
    """
    Удаляет компоненты, которые соприкасаются с краями изображения.

    Это защищает от захвата рамки фотографии, края стола
    и других объектов по границе кадра.
    """

    result = mask.copy()

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        result,
        connectivity=8,
    )

    height, width = result.shape

    for label in range(1, num_labels):
        x = stats[label, cv2.CC_STAT_LEFT]
        y = stats[label, cv2.CC_STAT_TOP]
        w = stats[label, cv2.CC_STAT_WIDTH]
        h = stats[label, cv2.CC_STAT_HEIGHT]

        touches_border = (
            x <= border_size
            or y <= border_size
            or x + w >= width - border_size
            or y + h >= height - border_size
        )

        if touches_border:
            result[labels == label] = 0

    return result


def _build_boundary_map(image: np.ndarray) -> np.ndarray:
    """
    Строит карту границ рисунка.

    Используются несколько независимых признаков.
    Нам не нужно понимать, какого цвета рыба.
    Нам нужно найти линии, которые образуют её внешний силуэт.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ---------------------------------------------------------
    # 1. Локальный контраст
    # ---------------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    blurred = cv2.GaussianBlur(
        enhanced,
        (5, 5),
        0,
    )

    # ---------------------------------------------------------
    # 2. Canny
    # ---------------------------------------------------------

    edges = cv2.Canny(
        blurred,
        25,
        85,
    )

    # ---------------------------------------------------------
    # 3. Adaptive threshold
    #
    # Хорошо работает для карандаша и тонких линий.
    # ---------------------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41,
        7,
    )

    # Убираем совсем мелкий шум.
    kernel_small = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3),
    )

    adaptive = cv2.morphologyEx(
        adaptive,
        cv2.MORPH_OPEN,
        kernel_small,
    )

    # ---------------------------------------------------------
    # 4. Цветовой/световой контраст
    #
    # Помогает с бежевыми, жёлтыми и цветными участками.
    # ---------------------------------------------------------

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB,
    )

    l_channel, a_channel, b_channel = cv2.split(lab)

    # Локальная разница яркости.
    background = cv2.GaussianBlur(
        l_channel,
        (0, 0),
        21,
    )

    local_difference = cv2.absdiff(
        l_channel,
        background,
    )

    color_signal = cv2.normalize(
        local_difference,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    _, color_mask = cv2.threshold(
        color_signal,
        18,
        255,
        cv2.THRESH_BINARY,
    )

    # Дополнительный цветовой сигнал.
    color_distance_a = cv2.absdiff(
        a_channel,
        cv2.GaussianBlur(a_channel, (0, 0), 21),
    )

    color_distance_b = cv2.absdiff(
        b_channel,
        cv2.GaussianBlur(b_channel, (0, 0), 21),
    )

    color_signal_2 = cv2.add(
        color_distance_a,
        color_distance_b,
    )

    color_signal_2 = cv2.normalize(
        color_signal_2,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    _, color_mask_2 = cv2.threshold(
        color_signal_2,
        15,
        255,
        cv2.THRESH_BINARY,
    )

    # ---------------------------------------------------------
    # 5. Объединяем признаки
    # ---------------------------------------------------------

    boundary = cv2.bitwise_or(
        edges,
        adaptive,
    )

    boundary = cv2.bitwise_or(
        boundary,
        color_mask,
    )

    boundary = cv2.bitwise_or(
        boundary,
        color_mask_2,
    )

    # ---------------------------------------------------------
    # 6. Закрываем разрывы внешнего контура
    #
    # Это ключевой этап.
    #
    # Если линия головы немного не соединена с телом,
    # контур всё равно должен стать единым.
    # ---------------------------------------------------------

    kernel_close_large = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (13, 13),
    )

    boundary = cv2.morphologyEx(
        boundary,
        cv2.MORPH_CLOSE,
        kernel_close_large,
    )

    kernel_close_medium = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (7, 7),
    )

    boundary = cv2.morphologyEx(
        boundary,
        cv2.MORPH_CLOSE,
        kernel_close_medium,
    )

    # Немного расширяем линии перед поиском единой области.
    boundary = cv2.dilate(
        boundary,
        cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5),
        ),
        iterations=1,
    )

    boundary = _remove_border_components(
        boundary,
        border_size=10,
    )

    return boundary


def _select_fish_region(boundary: np.ndarray) -> np.ndarray:
    """
    Превращает набор найденных линий в единое выделение рыбки.

    Здесь принципиально не используется анализ цвета внутри объекта.
    """

    height, width = boundary.shape
    image_area = height * width

    contours, _ = cv2.findContours(
        boundary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    if not contours:
        raise ValueError(
            "Не удалось построить границу рисунка."
        )

    candidates = []

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < image_area * 0.003:
            continue

        if area > image_area * 0.70:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        if w < 40 or h < 30:
            continue

        # Отношение заполнения.
        rect_area = max(w * h, 1)
        fill_ratio = area / rect_area

        # Слишком тонкие случайные линии отбрасываем.
        if fill_ratio < 0.03:
            continue

        candidates.append(
            {
                "contour": contour,
                "area": area,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "fill_ratio": fill_ratio,
            }
        )

    if not candidates:
        raise ValueError(
            "Не удалось найти область рыбки."
        )

    # ---------------------------------------------------------
    # Выбираем наиболее вероятную область рисунка.
    #
    # Не просто максимальную площадь.
    # Учитываем размеры и положение.
    # ---------------------------------------------------------

    def score(candidate):
        x = candidate["x"]
        y = candidate["y"]
        w = candidate["w"]
        h = candidate["h"]
        area = candidate["area"]

        center_x = x + w / 2
        center_y = y + h / 2

        image_center_x = width / 2
        image_center_y = height / 2

        center_distance = (
            abs(center_x - image_center_x) / width
            +
            abs(center_y - image_center_y) / height
        )

        size_score = area / image_area

        # Большая центральная область получает больше веса.
        return (
            size_score * 5.0
            - center_distance * 0.7
        )

    candidates.sort(
        key=score,
        reverse=True,
    )

    fish_contour = candidates[0]["contour"]

    # ---------------------------------------------------------
    # Создаём заполненную область.
    #
    # ВЕСЬ объект внутри внешней границы считается рыбкой.
    # ---------------------------------------------------------

    mask = np.zeros(
        (height, width),
        dtype=np.uint8,
    )

    cv2.drawContours(
        mask,
        [fish_contour],
        -1,
        255,
        thickness=cv2.FILLED,
    )

    # ---------------------------------------------------------
    # Небольшое сглаживание края.
    # ---------------------------------------------------------

    mask = cv2.GaussianBlur(
        mask,
        (5, 5),
        0,
    )

    # Возвращаем нормальную бинарную маску,
    # чтобы внутри рыбы alpha не становился полупрозрачным.
    _, mask = cv2.threshold(
        mask,
        80,
        255,
        cv2.THRESH_BINARY,
    )

    return mask


def detect_fish_outline(image: np.ndarray) -> np.ndarray:
    """
    Профессиональный внешний силуэт рыбки.

    Основной принцип:

        НЕ определяем рыбку по цвету.

        Сначала определяем её внешнюю границу.

        После этого вся область внутри границы
        считается рыбкой.

    Поэтому:
        - чёрная голова сохраняется;
        - бежевая голова сохраняется;
        - светлое тело сохраняется;
        - цветные участки сохраняются;
        - внутренние детали сохраняются;
        - фон за внешней границей становится прозрачным.
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Изображение пустое."
        )

    boundary = _build_boundary_map(
        image
    )

    mask = _select_fish_region(
        boundary
    )

    if mask is None or not np.any(mask > 0):
        raise ValueError(
            "Не удалось выделить рыбку."
        )

    coverage = (
        np.count_nonzero(mask)
        /
        mask.size
    )

    if coverage > 0.75:
        raise ValueError(
            "Выделение захватило слишком большую область."
        )

    return mask