import cv2
import numpy as np
from pathlib import Path

from app.image_processing.fish_outline import (
    detect_fish_outline,
)

from app.image_processing.fish_outline_v3 import (
    detect_fish_outline_v3,
)


def _binary(mask: np.ndarray) -> np.ndarray:
    """Приводит маску к бинарному одноканальному виду."""

    if mask is None:
        raise ValueError("Маска отсутствует.")

    if mask.ndim == 3:
        if mask.shape[2] == 4:
            mask = cv2.cvtColor(
                mask,
                cv2.COLOR_BGRA2GRAY,
            )
        else:
            mask = cv2.cvtColor(
                mask,
                cv2.COLOR_BGR2GRAY,
            )

    if mask.ndim != 2:
        raise ValueError(
            "Маска должна быть одноканальной."
        )

    mask = mask.astype(np.uint8)

    result = np.zeros_like(
        mask,
        dtype=np.uint8,
    )

    result[mask > 127] = 255

    return result


def _bbox(mask: np.ndarray):
    """Возвращает bounding box маски."""

    mask = _binary(mask)

    points = cv2.findNonZero(mask)

    if points is None:
        return None

    x, y, w, h = cv2.boundingRect(points)

    return (
        int(x),
        int(y),
        int(x + w - 1),
        int(y + h - 1),
    )


def _expand_bbox(
    bbox,
    image_shape,
    padding_ratio=0.08,
):
    """
    Немного расширяет область рыбки.
    """

    if bbox is None:
        return None

    x1, y1, x2, y2 = bbox

    height, width = image_shape[:2]

    w = x2 - x1 + 1
    h = y2 - y1 + 1

    pad_x = max(
        20,
        int(w * padding_ratio),
    )

    pad_y = max(
        20,
        int(h * padding_ratio),
    )

    x1 = max(
        0,
        x1 - pad_x,
    )

    y1 = max(
        0,
        y1 - pad_y,
    )

    x2 = min(
        width - 1,
        x2 + pad_x,
    )

    y2 = min(
        height - 1,
        y2 + pad_y,
    )

    return (
        x1,
        y1,
        x2,
        y2,
    )


def _intersection(
    a: np.ndarray,
    b: np.ndarray,
) -> np.ndarray:
    """Общая часть двух масок."""

    a = _binary(a)
    b = _binary(b)

    return cv2.bitwise_and(
        a,
        b,
    )


def _union(
    a: np.ndarray,
    b: np.ndarray,
) -> np.ndarray:
    """Объединение двух масок."""

    a = _binary(a)
    b = _binary(b)

    return cv2.bitwise_or(
        a,
        b,
    )


def _near_core(
    candidate: np.ndarray,
    core: np.ndarray,
    distance: int,
) -> np.ndarray:
    """
    Берёт только те части candidate,
    которые находятся рядом с подтверждённым
    ядром рыбки.
    """

    candidate = _binary(candidate)
    core = _binary(core)

    distance = max(
        1,
        int(distance),
    )

    kernel_size = (
        distance * 2 + 1
    )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (
            kernel_size,
            kernel_size,
        ),
    )

    expanded_core = cv2.dilate(
        core,
        kernel,
        iterations=1,
    )

    return cv2.bitwise_and(
        candidate,
        expanded_core,
    )


def _combine_v2_v3(
    v2: np.ndarray,
    v3: np.ndarray,
    image: np.ndarray,
) -> np.ndarray:

    v2 = _binary(v2)
    v3 = _binary(v3)

    v2_area = cv2.countNonZero(v2)
    v3_area = cv2.countNonZero(v3)

    print(
        "V4: площадь V2:",
        v2_area,
        "пикселей",
    )

    print(
        "V4: площадь V3:",
        v3_area,
        "пикселей",
    )

    # =====================================================
    # Обе версии работают
    # =====================================================

    if (
        v2_area > 0
        and
        v3_area > 0
    ):

        core = _intersection(
            v2,
            v3,
        )

        core_area = cv2.countNonZero(
            core
        )

        print(
            "V4: общая область V2 + V3:",
            core_area,
            "пикселей",
        )

        # -------------------------------------------------
        # Есть общее ядро
        # -------------------------------------------------

        if core_area > 0:

            combo = core.copy()

            bbox2 = _bbox(v2)
            bbox3 = _bbox(v3)

            if bbox2 is not None:
                bbox2 = _expand_bbox(
                    bbox2,
                    image.shape,
                )

            if bbox3 is not None:
                bbox3 = _expand_bbox(
                    bbox3,
                    image.shape,
                )

            core_bbox = _bbox(core)

            if core_bbox is not None:

                cx1, cy1, cx2, cy2 = (
                    core_bbox
                )

                core_width = (
                    cx2 - cx1 + 1
                )

                core_height = (
                    cy2 - cy1 + 1
                )

                distance = int(
                    max(
                        core_width,
                        core_height,
                    )
                    * 0.12
                )

                distance = max(
                    25,
                    min(
                        distance,
                        100,
                    ),
                )

            else:

                distance = 50

            print(
                "V4: радиус объединения:",
                distance,
            )

            # -------------------------------------------------
            # Добавляем части V2 рядом с ядром
            # -------------------------------------------------

            v2_near = _near_core(
                v2,
                core,
                distance,
            )

            combo = _union(
                combo,
                v2_near,
            )

            # -------------------------------------------------
            # Добавляем части V3 рядом с ядром
            # -------------------------------------------------

            v3_near = _near_core(
                v3,
                core,
                distance,
            )

            combo = _union(
                combo,
                v3_near,
            )

            # -------------------------------------------------
            # Берём большую маску как дополнительный источник
            # -------------------------------------------------

            if v3_area > v2_area:
                larger = v3
                larger_name = "V3"
            else:
                larger = v2
                larger_name = "V2"

            larger_near = _near_core(
                larger,
                combo,
                distance,
            )

            combo = _union(
                combo,
                larger_near,
            )

            print(
                "V4: основная маска:",
                larger_name,
            )

            return _binary(combo)

        # -------------------------------------------------
        # Пересечения нет
        # -------------------------------------------------

        print(
            "V4: пересечение отсутствует."
        )

        if v2_area >= v3_area:

            print(
                "V4: берём V2."
            )

            return v2

        print(
            "V4: берём V3."
        )

        return v3

    # =====================================================
    # Работает только V2
    # =====================================================

    if v2_area > 0:

        print(
            "V4: используется только V2."
        )

        return v2

    # =====================================================
    # Работает только V3
    # =====================================================

    if v3_area > 0:

        print(
            "V4: используется только V3."
        )

        return v3

    raise ValueError(
        "V2 и V3 не смогли выделить рыбку."
    )


def _repair_mask(
    mask: np.ndarray,
) -> np.ndarray:
    """
    Мягкое восстановление маски.
    """

    mask = _binary(mask)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (7, 7),
    )

    repaired = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
    )

    repaired = cv2.GaussianBlur(
        repaired,
        (3, 3),
        0,
    )

    _, repaired = cv2.threshold(
        repaired,
        80,
        255,
        cv2.THRESH_BINARY,
    )

    return _binary(repaired)


def detect_fish_outline_v4(
    image: np.ndarray,
    debug_dir=None,
) -> np.ndarray:

    if image is None or image.size == 0:
        raise ValueError(
            "Изображение пустое."
        )

    debug_path = None

    if debug_dir is not None:

        debug_path = Path(
            debug_dir
        )

        debug_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # V2
    # =====================================================

    v2_error = None

    try:

        v2_mask = detect_fish_outline(
            image
        )

        v2_mask = _binary(
            v2_mask
        )

        print(
            "V2: OK"
        )

    except Exception as error:

        v2_mask = np.zeros(
            image.shape[:2],
            dtype=np.uint8,
        )

        v2_error = str(
            error
        )

        print(
            "V2: ОШИБКА:",
            v2_error,
        )

    # =====================================================
    # V3
    # =====================================================

    v3_error = None

    try:

        v3_mask = detect_fish_outline_v3(
            image
        )

        v3_mask = _binary(
            v3_mask
        )

        print(
            "V3: OK"
        )

    except Exception as error:

        v3_mask = np.zeros(
            image.shape[:2],
            dtype=np.uint8,
        )

        v3_error = str(
            error
        )

        print(
            "V3: ОШИБКА:",
            v3_error,
        )

    # =====================================================
    # DEBUG V2 / V3
    # =====================================================

    if debug_path is not None:

        cv2.imwrite(
            str(
                debug_path
                / "01_v2.png"
            ),
            v2_mask,
        )

        cv2.imwrite(
            str(
                debug_path
                / "02_v3.png"
            ),
            v3_mask,
        )

    # =====================================================
    # COMBINE V2 + V3
    # =====================================================

    combo = _combine_v2_v3(
        v2_mask,
        v3_mask,
        image,
    )

    combo = _binary(
        combo
    )

    if debug_path is not None:

        cv2.imwrite(
            str(
                debug_path
                / "03_combo_raw.png"
            ),
            combo,
        )

    # =====================================================
    # REPAIR
    # =====================================================

    final_mask = _repair_mask(
        combo
    )

    # =====================================================
    # ПРОВЕРКА
    # =====================================================

    final_mask = _binary(
        final_mask
    )

    coverage = (
        cv2.countNonZero(
            final_mask
        )
        /
        final_mask.size
    )

    print(
        "V4: покрытие:",
        f"{coverage * 100:.2f}%",
    )

    if coverage < 0.001:

        raise ValueError(
            "Рыбка получилась слишком маленькой."
        )

    if coverage > 0.75:

        raise ValueError(
            "Выделение захватило слишком большую область."
        )

    # =====================================================
    # DEBUG FINAL MASK
    # =====================================================

    if debug_path is not None:

        cv2.imwrite(
            str(
                debug_path
                / "04_final_mask.png"
            ),
            final_mask,
        )

    # =====================================================
    # DEBUG RGBA
    #
    # Это только отладочный файл.
    # В pipeline мы его НЕ возвращаем.
    # =====================================================

    rgba = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2BGRA,
    )

    rgba[:, :, 3] = final_mask

    if debug_path is not None:

        cv2.imwrite(
            str(
                debug_path
                / "05_final_rgba.png"
            ),
            rgba,
        )

        # -------------------------------------------------
        # Preview на белом фоне
        # -------------------------------------------------

        white = np.full_like(
            image,
            255,
        )

        alpha = (
            final_mask.astype(
                np.float32
            )
            / 255.0
        )

        alpha_3 = np.dstack(
            [
                alpha,
                alpha,
                alpha,
            ]
        )

        preview = (
            image.astype(
                np.float32
            )
            * alpha_3
            +
            white.astype(
                np.float32
            )
            * (
                1.0
                -
                alpha_3
            )
        )

        preview = np.clip(
            preview,
            0,
            255,
        ).astype(
            np.uint8
        )

        cv2.imwrite(
            str(
                debug_path
                / "06_preview_white.jpg"
            ),
            preview,
        )

        # -------------------------------------------------
        # Информация
        # -------------------------------------------------

        print(
            "V2:",
            "OK"
            if v2_error is None
            else v2_error,
        )

        print(
            "V3:",
            "OK"
            if v3_error is None
            else v3_error,
        )

    # =====================================================
    # ВАЖНО:
    # V4 возвращает ТОЛЬКО МАСКУ.
    #
    # Pipeline дальше сам создаёт RGBA:
    #
    # V4 → mask
    #     ↓
    # crop
    #     ↓
    # create_rgba
    #     ↓
    # resize
    # =====================================================

    return final_mask