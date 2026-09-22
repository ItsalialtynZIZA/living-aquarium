import cv2
import numpy as np


def _prepare_mask(alpha: np.ndarray) -> np.ndarray:
    """Создаёт чистую маску рыбки из alpha-канала."""

    mask = np.zeros_like(alpha, dtype=np.uint8)
    mask[alpha > 50] = 255

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        raise ValueError(
            "Контур рыбки не найден."
        )

    largest = max(
        contours,
        key=cv2.contourArea
    )

    clean = np.zeros_like(mask)

    cv2.drawContours(
        clean,
        [largest],
        -1,
        255,
        thickness=-1
    )

    return clean


def _get_axis_and_center(
    contour: np.ndarray
):
    """Определяет центр и главную ось рыбки."""

    points = (
        contour
        .reshape(-1, 2)
        .astype(np.float32)
    )

    moments = cv2.moments(contour)

    if moments["m00"] == 0:
        raise ValueError(
            "Не удалось определить центр рыбки."
        )

    cx = (
        moments["m10"]
        /
        moments["m00"]
    )

    cy = (
        moments["m01"]
        /
        moments["m00"]
    )

    center = np.array(
        [cx, cy],
        dtype=np.float32
    )

    mean, eigenvectors, eigenvalues = (
        cv2.PCACompute2(
            points,
            mean=None
        )
    )

    axis = eigenvectors[0].astype(
        np.float32
    )

    axis /= np.linalg.norm(axis)

    return center, axis, points


def _project_points(
    points: np.ndarray,
    center: np.ndarray,
    axis: np.ndarray
):
    """
    Переводит точки в систему координат рыбки.

    longitudinal:
        положение вдоль тела.

    lateral:
        положение поперёк тела.
    """

    normal = np.array(
        [
            -axis[1],
            axis[0]
        ],
        dtype=np.float32
    )

    relative = points - center

    longitudinal = np.dot(
        relative,
        axis
    )

    lateral = np.dot(
        relative,
        normal
    )

    return longitudinal, lateral


def _endpoint_widths(
    points: np.ndarray,
    center: np.ndarray,
    axis: np.ndarray,
):
    """Измеряет ширину рыбки возле обоих концов."""

    longitudinal, lateral = _project_points(
        points,
        center,
        axis
    )

    min_long = float(
        np.min(longitudinal)
    )

    max_long = float(
        np.max(longitudinal)
    )

    length = max_long - min_long

    if length <= 1:
        return 0.0, 0.0

    zone = length * 0.16

    left_points = lateral[
        longitudinal < min_long + zone
    ]

    right_points = lateral[
        longitudinal > max_long - zone
    ]

    if len(left_points) < 3:
        left_width = 0.0
    else:
        left_width = float(
            np.percentile(
                left_points,
                95
            )
            -
            np.percentile(
                left_points,
                5
            )
        )

    if len(right_points) < 3:
        right_width = 0.0
    else:
        right_width = float(
            np.percentile(
                right_points,
                95
            )
            -
            np.percentile(
                right_points,
                5
            )
        )

    return left_width, right_width


def _cross_section_profile(
    points: np.ndarray,
    center: np.ndarray,
    axis: np.ndarray,
):
    """
    Получает профиль ширины рыбки вдоль главной оси.

    Возвращает ширины в нескольких зонах.
    """

    longitudinal, lateral = _project_points(
        points,
        center,
        axis
    )

    min_long = float(
        np.min(longitudinal)
    )

    max_long = float(
        np.max(longitudinal)
    )

    length = max_long - min_long

    if length <= 1:
        return []

    profile = []

    zones = 10

    for i in range(zones):

        start = (
            min_long
            +
            length * i / zones
        )

        end = (
            min_long
            +
            length * (i + 1) / zones
        )

        selected = lateral[
            (longitudinal >= start)
            &
            (longitudinal < end)
        ]

        if len(selected) < 3:
            profile.append(0.0)
            continue

        width = (
            np.percentile(
                selected,
                95
            )
            -
            np.percentile(
                selected,
                5
            )
        )

        profile.append(
            float(width)
        )

    return profile


def _shape_score(
    profile: list[float]
):
    """
    Анализирует профиль тела.

    Голова обычно:
        широкая и округлая.

    Хвост обычно:
        соединяется с более узкой частью тела.
    """

    if len(profile) < 6:
        return 0.0, 0.0

    profile = np.array(
        profile,
        dtype=np.float32
    )

    maximum = float(
        np.max(profile)
    )

    if maximum <= 1:
        return 0.0, 0.0

    profile /= maximum

    left_head = float(
        np.mean(profile[0:3])
    )

    right_head = float(
        np.mean(profile[-3:])
    )

    left_body = float(
        np.mean(profile[3:6])
    )

    right_body = float(
        np.mean(profile[4:7])
    )

    left_score = (
        left_head
        -
        left_body * 0.55
    )

    right_score = (
        right_head
        -
        right_body * 0.55
    )

    return (
        float(left_score),
        float(right_score)
    )


def _tail_shape_score(
    mask: np.ndarray,
    center: np.ndarray,
    axis: np.ndarray,
):
    """
    Ищет признаки хвоста.

    Хвост часто имеет:
        - сужение;
        - раздвоение;
        - V-образную форму.

    Возвращает:
        score_left,
        score_right
    """

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return 0.0, 0.0

    contour = max(
        contours,
        key=cv2.contourArea
    )

    points = (
        contour
        .reshape(-1, 2)
        .astype(np.float32)
    )

    longitudinal, lateral = _project_points(
        points,
        center,
        axis
    )

    min_long = float(
        np.min(longitudinal)
    )

    max_long = float(
        np.max(longitudinal)
    )

    length = max_long - min_long

    if length <= 1:
        return 0.0, 0.0

    # Узкая зона возле тела.
    left_body_zone = (
        (longitudinal > min_long + length * 0.12)
        &
        (longitudinal < min_long + length * 0.30)
    )

    right_body_zone = (
        (longitudinal < max_long - length * 0.12)
        &
        (longitudinal > max_long - length * 0.30)
    )

    # Самые крайние зоны.
    left_tip_zone = (
        longitudinal < min_long + length * 0.12
    )

    right_tip_zone = (
        longitudinal > max_long - length * 0.12
    )

    def width(zone):
        values = lateral[zone]

        if len(values) < 3:
            return 0.0

        return float(
            np.percentile(values, 95)
            -
            np.percentile(values, 5)
        )

    left_body_width = width(
        left_body_zone
    )

    right_body_width = width(
        right_body_zone
    )

    left_tip_width = width(
        left_tip_zone
    )

    right_tip_width = width(
        right_tip_zone
    )

    left_score = 0.0
    right_score = 0.0

    if left_body_width > 1:

        ratio = (
            left_tip_width
            /
            left_body_width
        )

        if ratio < 0.75:
            left_score += 0.6

        if ratio < 0.55:
            left_score += 0.25

    if right_body_width > 1:

        ratio = (
            right_tip_width
            /
            right_body_width
        )

        if ratio < 0.75:
            right_score += 0.6

        if ratio < 0.55:
            right_score += 0.25

    return (
        float(
            np.clip(
                left_score,
                0,
                1
            )
        ),
        float(
            np.clip(
                right_score,
                0,
                1
            )
        )
    )


def _detail_score(
    rgba: np.ndarray,
    mask: np.ndarray,
    center: np.ndarray,
    axis: np.ndarray,
):
    """
    Ищет тёмные внутренние детали.

    Глаз или другие детали головы
    могут находиться ближе к голове,
    чем к хвосту.
    """

    bgr = rgba[:, :, :3]

    gray = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2GRAY
    )

    inside = mask > 0

    if not np.any(inside):
        return 0.0, 0.0

    # Эрозия убирает контур,
    # чтобы внешний контур рыбы
    # не считался глазом.
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (11, 11)
    )

    inner = cv2.erode(
        mask,
        kernel,
        iterations=1
    )

    inner_pixels = gray[
        inner > 0
    ]

    if len(inner_pixels) < 20:
        return 0.0, 0.0

    threshold = float(
        np.percentile(
            inner_pixels,
            25
        )
    )

    dark = (
        (gray < threshold)
        &
        (inner > 0)
    )

    ys, xs = np.where(
        dark
    )

    if len(xs) < 3:
        return 0.0, 0.0

    points = np.column_stack(
        [xs, ys]
    ).astype(np.float32)

    longitudinal, _ = _project_points(
        points,
        center,
        axis
    )

    fish_points = np.column_stack(
        np.where(mask > 0)[::-1]
    ).astype(np.float32)

    fish_longitudinal, _ = _project_points(
        fish_points,
        center,
        axis
    )

    min_long = float(
        np.min(fish_longitudinal)
    )

    max_long = float(
        np.max(fish_longitudinal)
    )

    length = max_long - min_long

    if length <= 1:
        return 0.0, 0.0

    left_zone = (
        longitudinal
        <
        min_long + length * 0.30
    )

    right_zone = (
        longitudinal
        >
        max_long - length * 0.30
    )

    left_count = int(
        np.sum(left_zone)
    )

    right_count = int(
        np.sum(right_zone)
    )

    total = max(
        1,
        len(points)
    )

    left_score = (
        left_count / total
    )

    right_score = (
        right_count / total
    )

    return (
        float(
            np.clip(
                left_score * 4,
                0,
                1
            )
        ),
        float(
            np.clip(
                right_score * 4,
                0,
                1
            )
        )
    )


def detect_fish_orientation(
    rgba: np.ndarray
) -> dict:
    """
    Определяет предполагаемое направление головы рыбки.

    direction:
        1  = голова предполагается справа
        -1 = голова предполагается слева

    confidence:
        0..1

    Используются:
        - форма тела;
        - ширина концов;
        - профиль тела;
        - признаки хвоста;
        - внутренние детали.
    """

    if rgba is None or rgba.size == 0:
        raise ValueError(
            "Изображение рыбки пустое."
        )

    if rgba.ndim != 3:
        raise ValueError(
            "Ожидается изображение с 4 каналами."
        )

    if rgba.shape[2] != 4:
        raise ValueError(
            "Ожидается RGBA/BGRA изображение."
        )

    alpha = rgba[:, :, 3]

    mask = _prepare_mask(
        alpha
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        raise ValueError(
            "Контур рыбки не найден."
        )

    contour = max(
        contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(
        contour
    )

    if area < 100:
        raise ValueError(
            "Контур рыбки слишком маленький."
        )

    center, axis, points = (
        _get_axis_and_center(
            contour
        )
    )

    # ------------------------------------------
    # 1. Ширина концов
    # ------------------------------------------

    left_width, right_width = (
        _endpoint_widths(
            points,
            center,
            axis
        )
    )

    width_difference = (
        right_width
        -
        left_width
    )

    width_total = (
        right_width
        +
        left_width
        +
        1e-6
    )

    width_signal = (
        width_difference
        /
        width_total
    )

    # ------------------------------------------
    # 2. Профиль тела
    # ------------------------------------------

    profile = _cross_section_profile(
        points,
        center,
        axis
    )

    left_shape, right_shape = (
        _shape_score(
            profile
        )
    )

    shape_signal = (
        right_shape
        -
        left_shape
    )

    # ------------------------------------------
    # 3. Хвост
    # ------------------------------------------

    left_tail, right_tail = (
        _tail_shape_score(
            mask,
            center,
            axis
        )
    )

    # Если слева больше признаков хвоста,
    # значит голова вероятнее справа.
    tail_signal = (
        left_tail
        -
        right_tail
    )

    # ------------------------------------------
    # 4. Внутренние детали
    # ------------------------------------------

    left_detail, right_detail = (
        _detail_score(
            rgba,
            mask,
            center,
            axis
        )
    )

    detail_signal = (
        right_detail
        -
        left_detail
    )

    # ------------------------------------------
    # 5. Общий score
    # ------------------------------------------

    # Положительное значение:
    # голова справа.

    total_score = (
        width_signal * 0.25
        +
        shape_signal * 0.25
        +
        tail_signal * 0.30
        +
        detail_signal * 0.20
    )

    # ------------------------------------------
    # Направление
    # ------------------------------------------

    if total_score >= 0:
        direction = 1
    else:
        direction = -1

    # ------------------------------------------
    # Уверенность
    # ------------------------------------------

    confidence = abs(
        total_score
    )

    confidence = float(
        np.clip(
            confidence,
            0.0,
            1.0
        )
    )

    # Если признаки сильно конфликтуют,
    # уменьшаем уверенность.

    signals = np.array(
        [
            width_signal,
            shape_signal,
            tail_signal,
            detail_signal,
        ],
        dtype=np.float32
    )

    signs = np.sign(
        signals[
            np.abs(signals) > 0.05
        ]
    )

    if len(signs) >= 2:

        positive = np.sum(
            signs > 0
        )

        negative = np.sum(
            signs < 0
        )

        conflict = min(
            positive,
            negative
        )

        if conflict > 0:

            confidence *= 0.65

    return {
        "direction": int(
            direction
        ),

        "confidence": float(
            confidence
        ),

        "angle": float(
            np.degrees(
                np.arctan2(
                    axis[1],
                    axis[0]
                )
            )
        ),

        "center": (
            float(center[0]),
            float(center[1])
        ),

        "width_left": float(
            left_width
        ),

        "width_right": float(
            right_width
        ),

        "shape_left": float(
            left_shape
        ),

        "shape_right": float(
            right_shape
        ),

        "tail_left": float(
            left_tail
        ),

        "tail_right": float(
            right_tail
        ),

        "detail_left": float(
            left_detail
        ),

        "detail_right": float(
            right_detail
        ),

        "score": float(
            total_score
        ),
    }