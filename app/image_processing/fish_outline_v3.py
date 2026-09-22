import cv2
import numpy as np


def _largest_center_component(mask: np.ndarray) -> np.ndarray:
    """
    Оставляет наиболее вероятную область рисунка.
    Компоненты, касающиеся края фотографии, удаляются.
    """

    h, w = mask.shape
    result = np.zeros_like(mask)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8,
    )

    candidates = []

    for label in range(1, num_labels):
        x = stats[label, cv2.CC_STAT_LEFT]
        y = stats[label, cv2.CC_STAT_TOP]
        width = stats[label, cv2.CC_STAT_WIDTH]
        height = stats[label, cv2.CC_STAT_HEIGHT]
        area = stats[label, cv2.CC_STAT_AREA]

        if area < 100:
            continue

        if (
            x <= 3
            or y <= 3
            or x + width >= w - 3
            or y + height >= h - 3
        ):
            continue

        cx, cy = centroids[label]

        center_distance = (
            ((cx - w / 2) / w) ** 2
            + ((cy - h / 2) / h) ** 2
        ) ** 0.5

        candidates.append(
            (
                area * (1.0 - min(center_distance, 0.8)),
                label,
            )
        )

    if not candidates:
        return result

    candidates.sort(
        reverse=True
    )

    # Берём несколько крупных близких компонентов,
    # потому что карандашная рыбка может состоять
    # из отдельных линий.
    selected = [
        label
        for _, label in candidates[:12]
    ]

    for label in selected:
        result[labels == label] = 255

    return result


def _build_pencil_mask(image: np.ndarray) -> np.ndarray:
    """
    Детектор именно карандашных/чёрных линий.

    Использует не цвет рыбки, а локальную разницу
    между карандашом и бумагой.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    # Немного подавляем мелкий шум камеры.
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0,
    )

    # ---------------------------------------------------------
    # Локальное затемнение.
    #
    # Карандаш обычно значительно темнее окружающей бумаги.
    # ---------------------------------------------------------

    background = cv2.GaussianBlur(
        gray,
        (0, 0),
        17,
    )

    dark_difference = cv2.subtract(
        background,
        gray,
    )

    dark_difference = cv2.normalize(
        dark_difference,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    _, dark_mask = cv2.threshold(
        dark_difference,
        18,
        255,
        cv2.THRESH_BINARY,
    )

    # ---------------------------------------------------------
    # Adaptive threshold.
    #
    # Второй независимый источник карандашных линий.
    # ---------------------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41,
        8,
    )

    # ---------------------------------------------------------
    # Canny.
    #
    # Помогает восстановить контур там, где карандаш
    # слишком светлый для threshold.
    # ---------------------------------------------------------

    edges = cv2.Canny(
        gray,
        18,
        65,
    )

    # ---------------------------------------------------------
    # Объединяем.
    # ---------------------------------------------------------

    pencil = cv2.bitwise_or(
        dark_mask,
        adaptive,
    )

    pencil = cv2.bitwise_or(
        pencil,
        edges,
    )

    # ---------------------------------------------------------
    # Убираем мелкий шум.
    # ---------------------------------------------------------

    small_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3),
    )

    pencil = cv2.morphologyEx(
        pencil,
        cv2.MORPH_OPEN,
        small_kernel,
    )

    # ---------------------------------------------------------
    # Самый важный этап:
    # соединяем небольшие разрывы карандашной линии.
    # ---------------------------------------------------------

    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (9, 9),
    )

    pencil = cv2.morphologyEx(
        pencil,
        cv2.MORPH_CLOSE,
        close_kernel,
    )

    # Немного расширяем линии.
    pencil = cv2.dilate(
        pencil,
        cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5),
        ),
        iterations=1,
    )

    # Убираем случайные компоненты.
    pencil = _largest_center_component(
        pencil
    )

    return pencil


def _build_fish_envelope(
    pencil_mask: np.ndarray,
) -> np.ndarray:
    """
    Формирует внешний силуэт из карандашных линий.

    Мы не пытаемся определить цвет или содержимое рыбки.
    Наша задача — получить область, ограниченную её контуром.
    """

    h, w = pencil_mask.shape
    image_area = h * w

    # Ещё раз соединяем части одного рисунка.
    envelope = cv2.morphologyEx(
        pencil_mask,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (17, 17),
        ),
    )

    envelope = cv2.dilate(
        envelope,
        cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (9, 9),
        ),
        iterations=1,
    )

    contours, _ = cv2.findContours(
        envelope,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    if not contours:
        raise ValueError(
            "Карандашный контур рыбки не найден."
        )

    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < image_area * 0.002:
            continue

        if area > image_area * 0.65:
            continue

        x, y, width, height = cv2.boundingRect(
            contour
        )

        if width < 50 or height < 30:
            continue

        rect_area = max(
            width * height,
            1,
        )

        fill_ratio = area / rect_area

        cx = x + width / 2
        cy = y + height / 2

        center_distance = (
            abs(cx - w / 2) / w
            +
            abs(cy - h / 2) / h
        )

        # Для карандашной рыбки не требуем большого
        # fill_ratio. Это принципиально.
        score = (
            area / image_area * 4.0
            + min(fill_ratio, 0.8)
            - center_distance * 0.5
        )

        candidates.append(
            (
                score,
                contour,
            )
        )

    if not candidates:
        raise ValueError(
            "Не удалось сформировать область карандашной рыбки."
        )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    fish_contour = candidates[0][1]

    mask = np.zeros(
        (h, w),
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
    # Слегка расширяем внешний силуэт.
    #
    # Это защищает светлые края головы/хвоста,
    # которые могли находиться непосредственно возле линии.
    # ---------------------------------------------------------

    mask = cv2.dilate(
        mask,
        cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (7, 7),
        ),
        iterations=1,
    )

    # Сглаживаем только край.
    mask = cv2.GaussianBlur(
        mask,
        (5, 5),
        0,
    )

    _, mask = cv2.threshold(
        mask,
        80,
        255,
        cv2.THRESH_BINARY,
    )

    return mask


def detect_fish_outline_v3(
    image: np.ndarray,
) -> np.ndarray:
    """
    V3 — выделение рыбки по карандашному/чёрному контуру.

    Принцип:

        карандашные линии
              ↓
        соединение разрывов
              ↓
        внешний envelope
              ↓
        заполненная область
              ↓
        оригинальные цвета внутри сохраняются

    Цвет внутри силуэта не используется для удаления пикселей.
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Изображение пустое."
        )

    pencil_mask = _build_pencil_mask(
        image
    )

    if not np.any(pencil_mask):
        raise ValueError(
            "Карандашные линии не обнаружены."
        )

    fish_mask = _build_fish_envelope(
        pencil_mask
    )

    coverage = (
        np.count_nonzero(fish_mask)
        / fish_mask.size
    )

    if coverage < 0.003:
        raise ValueError(
            "Область рыбки слишком маленькая."
        )

    if coverage > 0.70:
        raise ValueError(
            "Алгоритм захватил слишком большую область."
        )

    return fish_mask