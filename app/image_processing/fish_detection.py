import cv2
import numpy as np


# ============================================================
# НАСТРОЙКИ
# ============================================================

# Минимальная площадь компонента.
MIN_COMPONENT_AREA = 8

# Минимальный размер компонента для анализа.
MIN_ANALYSIS_AREA = 20

# Насколько расширяем область найденного рисунка.
ROI_PADDING = 35

# Максимальная доля листа, которую может занимать рисунок.
# Это защита от ситуации, когда тень или шум захватили почти весь лист.
MAX_DRAWING_AREA_RATIO = 0.72


# ============================================================
# ОБЩИЕ ПРОВЕРКИ
# ============================================================

def _validate_image(image: np.ndarray) -> None:
    if image is None or image.size == 0:
        raise ValueError("Изображение пустое.")

    if len(image.shape) != 3:
        raise ValueError("Ожидается цветное изображение.")

    if image.shape[2] != 3:
        raise ValueError("Ожидается изображение BGR.")


# ============================================================
# GRAYSCALE
# ============================================================

def _get_gray(image: np.ndarray) -> np.ndarray:

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return gray


# ============================================================
# НОРМАЛИЗАЦИЯ ЛОКАЛЬНОГО КОНТРАСТА
# ============================================================

def _enhance_gray(gray: np.ndarray) -> np.ndarray:
    """
    Усиливает слабые карандашные линии.

    CLAHE полезен при:
    - слабом карандаше;
    - неравномерном освещении;
    - слегка мятой бумаге;
    - участках с разной яркостью.
    """

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    return enhanced


# ============================================================
# ЛОКАЛЬНАЯ НОРМАЛИЗАЦИЯ
# ============================================================

def _local_darkness(gray: np.ndarray) -> np.ndarray:
    """
    Выделяет объекты, которые темнее своего локального фона.

    Важный момент:
    большая плавная тень руки обычно меняется медленно,
    поэтому после вычитания локального фона её влияние уменьшается.
    """

    background = cv2.GaussianBlur(
        gray,
        (0, 0),
        sigmaX=15,
        sigmaY=15
    )

    dark = cv2.subtract(
        background,
        gray
    )

    dark = cv2.normalize(
        dark,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    return dark


# ============================================================
# BLACKHAT
# ============================================================

def _blackhat_mask(gray: np.ndarray) -> np.ndarray:
    """
    Blackhat хорошо подходит для карандашных линий.

    Он ищет тёмные элементы на светлом фоне.

    В отличие от простого threshold:
    - лучше переносит неравномерное освещение;
    - лучше видит слабый карандаш;
    - меньше реагирует на общий серый фон.
    """

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (21, 21)
    )

    blackhat = cv2.morphologyEx(
        gray,
        cv2.MORPH_BLACKHAT,
        kernel
    )

    # Небольшое усиление.
    blackhat = cv2.normalize(
        blackhat,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    return blackhat


# ============================================================
# КАРАНДАШ / ЧЁРНАЯ РУЧКА
# ============================================================

def _detect_line_evidence(
    image: np.ndarray,
    gray: np.ndarray
) -> np.ndarray:

    enhanced = _enhance_gray(gray)

    local_dark = _local_darkness(
        enhanced
    )

    blackhat = _blackhat_mask(
        enhanced
    )

    # --------------------------------------------------------
    # 1. Локальные тёмные элементы
    # --------------------------------------------------------

    _, local_mask = cv2.threshold(
        local_dark,
        22,
        255,
        cv2.THRESH_BINARY
    )

    # --------------------------------------------------------
    # 2. Blackhat
    # --------------------------------------------------------

    _, blackhat_mask = cv2.threshold(
        blackhat,
        18,
        255,
        cv2.THRESH_BINARY
    )

    # --------------------------------------------------------
    # 3. Adaptive Threshold
    # --------------------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        6
    )

    # --------------------------------------------------------
    # 4. Canny
    # --------------------------------------------------------

    blurred = cv2.GaussianBlur(
        enhanced,
        (5, 5),
        0
    )

    edges = cv2.Canny(
        blurred,
        25,
        85
    )

    # --------------------------------------------------------
    # Объединяем
    # --------------------------------------------------------

    result = cv2.bitwise_or(
        local_mask,
        blackhat_mask
    )

    result = cv2.bitwise_or(
        result,
        adaptive
    )

    result = cv2.bitwise_or(
        result,
        edges
    )

    # --------------------------------------------------------
    # Убираем одиночный шум
    # --------------------------------------------------------

    small_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    result = cv2.morphologyEx(
        result,
        cv2.MORPH_OPEN,
        small_kernel,
        iterations=1
    )

    # --------------------------------------------------------
    # Небольшое закрытие разрывов.
    #
    # НЕ делаем сильную заливку.
    # --------------------------------------------------------

    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    result = cv2.morphologyEx(
        result,
        cv2.MORPH_CLOSE,
        close_kernel,
        iterations=1
    )

    return result


# ============================================================
# ЦВЕТНОЙ РИСУНОК
# ============================================================

def _detect_color_evidence(
    image: np.ndarray
) -> np.ndarray:

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    saturation = hsv[:, :, 1]

    a_channel = lab[:, :, 1]
    b_channel = lab[:, :, 2]

    # --------------------------------------------------------
    # SATURATION
    #
    # Важная причина, почему жёлтый маркер тоже работает:
    # мы не проверяем конкретный цвет.
    # --------------------------------------------------------

    saturation_mask = np.zeros_like(
        saturation
    )

    saturation_mask[
        saturation > 28
    ] = 255

    # --------------------------------------------------------
    # Цветовые каналы LAB.
    #
    # Помогают видеть слабые цветные рисунки.
    # --------------------------------------------------------

    color_variation_a = cv2.absdiff(
        a_channel,
        np.full_like(a_channel, 128)
    )

    color_variation_b = cv2.absdiff(
        b_channel,
        np.full_like(b_channel, 128)
    )

    color_variation = cv2.max(
        color_variation_a,
        color_variation_b
    )

    _, lab_mask = cv2.threshold(
        color_variation,
        10,
        255,
        cv2.THRESH_BINARY
    )

    # --------------------------------------------------------
    # Объединяем.
    # --------------------------------------------------------

    result = cv2.bitwise_or(
        saturation_mask,
        lab_mask
    )

    # --------------------------------------------------------
    # Убираем мелкий шум.
    # --------------------------------------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    result = cv2.morphologyEx(
        result,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    result = cv2.morphologyEx(
        result,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    return result


# ============================================================
# ОЦЕНКА ПЕРИМЕТРА / КРАЁВ
# ============================================================

def _remove_border_noise(
    mask: np.ndarray
) -> np.ndarray:

    binary = np.where(
        mask > 0,
        255,
        0
    ).astype(np.uint8)

    height, width = binary.shape

    num_labels, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )

    result = np.zeros_like(
        binary
    )

    for label in range(
        1,
        num_labels
    ):

        x = stats[
            label,
            cv2.CC_STAT_LEFT
        ]

        y = stats[
            label,
            cv2.CC_STAT_TOP
        ]

        w = stats[
            label,
            cv2.CC_STAT_WIDTH
        ]

        h = stats[
            label,
            cv2.CC_STAT_HEIGHT
        ]

        area = stats[
            label,
            cv2.CC_STAT_AREA
        ]

        if area < MIN_COMPONENT_AREA:
            continue

        # ----------------------------------------------------
        # Убираем элементы, касающиеся края.
        #
        # Это важно для:
        # - края фотографии;
        # - края бумаги;
        # - тёмного стола;
        # - чехла;
        # - пальцев возле края.
        # ----------------------------------------------------

        touches_border = (
            x <= 1
            or y <= 1
            or x + w >= width - 1
            or y + h >= height - 1
        )

        if touches_border:
            continue

        result[
            labels == label
        ] = 255

    return result


# ============================================================
# СОЕДИНЕНИЕ РАЗРОЗНЕННЫХ ЧАСТЕЙ
# ============================================================

def _connect_drawing_parts(
    mask: np.ndarray
) -> np.ndarray:

    # Небольшое расширение.
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    expanded = cv2.dilate(
        mask,
        kernel,
        iterations=1
    )

    # Соединяем близкие части рисунка.
    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (13, 13)
    )

    connected = cv2.morphologyEx(
        expanded,
        cv2.MORPH_CLOSE,
        close_kernel,
        iterations=2
    )

    return connected


# ============================================================
# ПОИСК ОБЛАСТИ ОСНОВНОГО РИСУНКА
# ============================================================

def _find_main_drawing_roi(
    evidence: np.ndarray
) -> tuple[int, int, int, int] | None:

    if evidence is None:
        return None

    if cv2.countNonZero(evidence) == 0:
        return None

    connected = _connect_drawing_parts(
        evidence
    )

    connected = _remove_border_noise(
        connected
    )

    if cv2.countNonZero(connected) == 0:
        return None

    contours, _ = cv2.findContours(
        connected,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    height, width = evidence.shape

    image_area = (
        width * height
    )

    candidates = []

    for contour in contours:

        contour_area = cv2.contourArea(
            contour
        )

        if contour_area < MIN_ANALYSIS_AREA:
            continue

        x, y, w, h = cv2.boundingRect(
            contour
        )

        bbox_area = w * h

        if bbox_area <= 0:
            continue

        # Слишком большая область — вероятнее всего
        # тень, артефакт или фон.
        if (
            bbox_area
            > image_area * MAX_DRAWING_AREA_RATIO
        ):
            continue

        roi = evidence[
            y:y + h,
            x:x + w
        ]

        evidence_pixels = cv2.countNonZero(
            roi
        )

        if evidence_pixels < 20:
            continue

        density = (
            evidence_pixels
            / float(bbox_area)
        )

        # ----------------------------------------------------
        # Центр листа.
        # ----------------------------------------------------

        center_x = x + w / 2.0
        center_y = y + h / 2.0

        normalized_x = abs(
            center_x - width / 2.0
        ) / max(
            width / 2.0,
            1.0
        )

        normalized_y = abs(
            center_y - height / 2.0
        ) / max(
            height / 2.0,
            1.0
        )

        centrality = max(
            0.0,
            1.0
            - (
                normalized_x
                + normalized_y
            ) / 2.0
        )

        # ----------------------------------------------------
        # Размер.
        # ----------------------------------------------------

        size_score = min(
            bbox_area
            / (
                image_area
                * 0.30
            ),
            1.0
        )

        # ----------------------------------------------------
        # Вытянутость.
        #
        # Рыба часто горизонтальная или слегка диагональная.
        # Но НЕ требуем этого жёстко.
        # ----------------------------------------------------

        aspect = max(
            w / max(h, 1),
            h / max(w, 1)
        )

        shape_score = min(
            aspect / 3.0,
            1.0
        )

        score = (
            density * 0.35
            + centrality * 0.25
            + size_score * 0.30
            + shape_score * 0.10
        )

        candidates.append(
            (
                score,
                x,
                y,
                w,
                h
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    best = candidates[0]

    return (
        best[1],
        best[2],
        best[3],
        best[4]
    )


# ============================================================
# СОЗДАНИЕ ОБЛАСТИ РИСУНКА
# ============================================================

def _limit_to_roi(
    mask: np.ndarray,
    roi: tuple[int, int, int, int],
    padding: int = ROI_PADDING
) -> np.ndarray:

    x, y, w, h = roi

    height, width = mask.shape

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

    result = np.zeros_like(
        mask
    )

    result[
        y1:y2,
        x1:x2
    ] = mask[
        y1:y2,
        x1:x2
    ]

    return result


# ============================================================
# УДАЛЕНИЕ МЕЛКИХ КОМПОНЕНТОВ
# ============================================================

def _remove_tiny_components(
    mask: np.ndarray,
    min_area: int = MIN_COMPONENT_AREA
) -> np.ndarray:

    binary = np.where(
        mask > 0,
        255,
        0
    ).astype(np.uint8)

    num_labels, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )

    result = np.zeros_like(
        binary
    )

    for label in range(
        1,
        num_labels
    ):

        area = stats[
            label,
            cv2.CC_STAT_AREA
        ]

        if area >= min_area:

            result[
                labels == label
            ] = 255

    return result


# ============================================================
# ЗАПОЛНЕННЫЕ ЦВЕТНЫЕ ОБЛАСТИ
# ============================================================

def _prepare_color_mask(
    color_mask: np.ndarray,
    roi: tuple[int, int, int, int]
) -> np.ndarray:

    limited = _limit_to_roi(
        color_mask,
        roi,
        padding=ROI_PADDING
    )

    # Соединяем разрывы цветной заливки.
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (7, 7)
    )

    limited = cv2.morphologyEx(
        limited,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    # Немного расширяем, чтобы не потерять
    # тонкие границы цветного рисунка.
    limited = cv2.dilate(
        limited,
        cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (3, 3)
        ),
        iterations=1
    )

    return limited


# ============================================================
# КАРАНДАШНАЯ МАСКА
# ============================================================

def _prepare_line_mask(
    line_mask: np.ndarray,
    roi: tuple[int, int, int, int]
) -> np.ndarray:

    """
    Для карандаша принципиально НЕ заполняем контуры.

    Сохраняем сами линии.
    """

    limited = _limit_to_roi(
        line_mask,
        roi,
        padding=ROI_PADDING
    )

    # Очень маленькое закрытие разрывов.
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    limited = cv2.morphologyEx(
        limited,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=1
    )

    # Не делаем сильный dilation.
    #
    # Иначе тонкая карандашная рыба превращается
    # в толстые полосы.
    limited = _remove_tiny_components(
        limited,
        min_area=5
    )

    return limited


# ============================================================
# ОПРЕДЕЛЕНИЕ ТИПА РИСУНКА
# ============================================================

def _calculate_drawing_statistics(
    line_mask: np.ndarray,
    color_mask: np.ndarray,
    roi: tuple[int, int, int, int]
) -> tuple[float, float]:

    x, y, w, h = roi

    height, width = line_mask.shape

    x1 = max(
        0,
        x - ROI_PADDING
    )

    y1 = max(
        0,
        y - ROI_PADDING
    )

    x2 = min(
        width,
        x + w + ROI_PADDING
    )

    y2 = min(
        height,
        y + h + ROI_PADDING
    )

    roi_area = max(
        (x2 - x1)
        * (y2 - y1),
        1
    )

    line_pixels = cv2.countNonZero(
        line_mask[
            y1:y2,
            x1:x2
        ]
    )

    color_pixels = cv2.countNonZero(
        color_mask[
            y1:y2,
            x1:x2
        ]
    )

    line_density = (
        line_pixels
        / roi_area
    )

    color_density = (
        color_pixels
        / roi_area
    )

    return (
        line_density,
        color_density
    )


# ============================================================
# ФИНАЛЬНАЯ МАСКА
# ============================================================

def _build_final_mask(
    line_mask: np.ndarray,
    color_mask: np.ndarray,
    roi: tuple[int, int, int, int]
) -> np.ndarray:

    line_part = _prepare_line_mask(
        line_mask,
        roi
    )

    color_part = _prepare_color_mask(
        color_mask,
        roi
    )

    # --------------------------------------------------------
    # Объединяем.
    #
    # Цветной рисунок:
    #     сохраняем заполненные области.
    #
    # Карандаш:
    #     сохраняем линии.
    # --------------------------------------------------------

    result = cv2.bitwise_or(
        line_part,
        color_part
    )

    # --------------------------------------------------------
    # Ещё одна очень мягкая очистка.
    # --------------------------------------------------------

    result = _remove_tiny_components(
        result,
        min_area=5
    )

    # --------------------------------------------------------
    # Небольшое сглаживание альфа-канала.
    # --------------------------------------------------------

    result = cv2.GaussianBlur(
        result,
        (3, 3),
        0
    )

    return result


# ============================================================
# FALLBACK
# ============================================================

def _fallback_detection(
    line_mask: np.ndarray,
    color_mask: np.ndarray
) -> np.ndarray:

    """
    Последний безопасный вариант.

    Если основной поиск ROI не сработал,
    мы не возвращаем пустую маску.

    Используем объединение доказательств.
    """

    result = cv2.bitwise_or(
        line_mask,
        color_mask
    )

    result = _remove_border_noise(
        result
    )

    result = _remove_tiny_components(
        result,
        min_area=5
    )

    if cv2.countNonZero(result) < 20:
        return np.zeros_like(
            line_mask
        )

    return result


# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def detect_fish(
    image: np.ndarray
) -> np.ndarray:

    """
    V3 — обнаружение рисунка рыбы.

    Поддерживает:

    - карандаш;
    - ручку;
    - маркер;
    - цветные рисунки;
    - закрашенные рисунки;
    - слабый контраст;
    - жёлтый маркер;
    - неравномерное освещение;
    - тени;
    - слегка мятую бумагу;
    - разорванные линии.

    Основной принцип:

        НЕ ищем идеальный силуэт рыбы.

    Вместо этого:

        1. ищем доказательства рисунка;
        2. определяем область рисунка;
        3. сохраняем все линии/цвета в этой области.

    Для карандашной рыбы белое пространство внутри
    не считается отдельным объектом.
    """

    _validate_image(
        image
    )

    gray = _get_gray(
        image
    )

    # ========================================================
    # 1. ЛИНИИ
    # ========================================================

    line_mask = _detect_line_evidence(
        image,
        gray
    )

    # ========================================================
    # 2. ЦВЕТ
    # ========================================================

    color_mask = _detect_color_evidence(
        image
    )

    # ========================================================
    # 3. Удаляем края
    # ========================================================

    line_mask = _remove_border_noise(
        line_mask
    )

    color_mask = _remove_border_noise(
        color_mask
    )

    # ========================================================
    # 4. Объединяем доказательства
    #
    # Для поиска ROI нам важно понять,
    # где вообще находится рисунок.
    # ========================================================

    evidence = cv2.bitwise_or(
        line_mask,
        color_mask
    )

    # ========================================================
    # 5. Ищем область основного рисунка
    # ========================================================

    roi = _find_main_drawing_roi(
        evidence
    )

    # ========================================================
    # 6. Основной режим
    # ========================================================

    if roi is not None:

        final_mask = _build_final_mask(
            line_mask,
            color_mask,
            roi
        )

    # ========================================================
    # 7. FALLBACK
    # ========================================================

    else:

        final_mask = _fallback_detection(
            line_mask,
            color_mask
        )

    # ========================================================
    # 8. Проверка результата
    # ========================================================

    non_zero = cv2.countNonZero(
        final_mask
    )

    if non_zero < 20:

        raise ValueError(
            "Не удалось надёжно отделить рисунок "
            "от бумаги A4. "
            "Попробуйте сфотографировать лист "
            "при хорошем освещении и без сильной тени."
        )

    # ========================================================
    # 9. Защита от ситуации, когда маска захватила почти
    # весь лист.
    # ========================================================

    total_pixels = (
        final_mask.shape[0]
        * final_mask.shape[1]
    )

    coverage = (
        non_zero
        / float(total_pixels)
    )

    if coverage > 0.75:

        # Пробуем более строгий вариант.
        strict = cv2.bitwise_and(
            line_mask,
            cv2.bitwise_or(
                line_mask,
                color_mask
            )
        )

        strict = _remove_border_noise(
            strict
        )

        strict = _remove_tiny_components(
            strict,
            min_area=5
        )

        if cv2.countNonZero(
            strict
        ) > 20:

            final_mask = strict

    # ========================================================
    # 10. Финальный uint8
    # ========================================================

    final_mask = np.clip(
        final_mask,
        0,
        255
    ).astype(
        np.uint8
    )

    return final_mask