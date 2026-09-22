from pathlib import Path

import cv2
import numpy as np

from app.image_processing.paper_detection import detect_paper
from app.image_processing.perspective import four_point_transform
from app.image_processing.lighting import normalize_lighting
from app.image_processing.fish_outline_v4 import detect_fish_outline_v4
from app.image_processing.rgba import create_rgba
from app.image_processing.crop_resize import resize_rgba
from app.image_processing.crop_drawing import crop_drawing


def process_drawing(
    image: np.ndarray,
    debug_dir: Path | None = None,
) -> np.ndarray:
    """
    Полностью обрабатывает фотографию детского рисунка.

    Этапы:

    1. Поиск листа A4.
    2. Исправление перспективы.
    3. Нормализация освещения.
    4. Выделение внешнего силуэта рыбки через V4.
       V4 объединяет V2 и V3.
    5. Crop вокруг рыбки.
    6. Создание прозрачного PNG.
    7. Resize.

    Возвращает:
        готовое изображение BGRA.
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Изображение пустое."
        )

    # =========================================================
    # DEBUG
    # =========================================================

    if debug_dir is not None:

        debug_dir = Path(debug_dir)

        debug_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        cv2.imwrite(
            str(
                debug_dir / "00_original.jpg"
            ),
            image,
        )

    # =========================================================
    # 1. ПОИСК ЛИСТА A4
    # =========================================================

    paper = detect_paper(
        image
    )

    if paper is None:
        raise ValueError(
            "Лист бумаги не найден."
        )

    if debug_dir is not None:

        debug_image = image.copy()

        points = paper.astype(
            np.int32
        ).reshape(
            (-1, 1, 2)
        )

        cv2.polylines(
            debug_image,
            [points],
            True,
            (0, 255, 0),
            5,
        )

        cv2.imwrite(
            str(
                debug_dir
                / "04_detected_sheet.jpg"
            ),
            debug_image,
        )

    # =========================================================
    # 2. ИСПРАВЛЕНИЕ ПЕРСПЕКТИВЫ
    # =========================================================

    warped = four_point_transform(
        image,
        paper,
    )

    if warped is None or warped.size == 0:
        raise ValueError(
            "Не удалось исправить перспективу листа."
        )

    if debug_dir is not None:

        cv2.imwrite(
            str(
                debug_dir
                / "05_warped.jpg"
            ),
            warped,
        )

    # =========================================================
    # 3. НОРМАЛИЗАЦИЯ ОСВЕЩЕНИЯ
    # =========================================================

    normalized = normalize_lighting(
        warped,
    )

    if normalized is None or normalized.size == 0:
        raise ValueError(
            "Не удалось нормализовать освещение."
        )

    if debug_dir is not None:

        cv2.imwrite(
            str(
                debug_dir
                / "06_normalized.jpg"
            ),
            normalized,
        )

    # =========================================================
    # 4. ВЫДЕЛЕНИЕ РЫБКИ
    #
    # V4 объединяет два проверенных алгоритма:
    #
    # V2 — хорошо работает с одной группой рисунков.
    # V3 — хорошо работает с другой группой рисунков.
    #
    # V4 использует их вместе.
    #
    # Внутри силуэта цвета НЕ удаляются.
    # Маска отвечает только за прозрачность фона.
    # =========================================================

    fish_mask = detect_fish_outline_v4(
        normalized,
        debug_dir=(
            debug_dir / "v4"
            if debug_dir is not None
            else None
        ),
    )

    if fish_mask is None or fish_mask.size == 0:
        raise ValueError(
            "Не удалось выделить рыбку."
        )

    if debug_dir is not None:

        cv2.imwrite(
            str(
                debug_dir
                / "10_fish_mask.png"
            ),
            fish_mask,
        )

    # =========================================================
    # 5. CROP РЫБКИ
    # =========================================================

    cropped_image = crop_drawing(
        normalized,
        fish_mask,
        padding=20,
    )

    cropped_mask = crop_drawing(
        fish_mask,
        fish_mask,
        padding=20,
    )

    if cropped_image is None or cropped_image.size == 0:
        raise ValueError(
            "Не удалось обрезать изображение рыбки."
        )

    if cropped_mask is None or cropped_mask.size == 0:
        raise ValueError(
            "Не удалось обрезать маску рыбки."
        )

    if debug_dir is not None:

        cv2.imwrite(
            str(
                debug_dir
                / "12_cropped_image.jpg"
            ),
            cropped_image,
        )

        cv2.imwrite(
            str(
                debug_dir
                / "12_cropped_mask.png"
            ),
            cropped_mask,
        )

    # =========================================================
    # 6. СОЗДАНИЕ RGBA
    #
    # Исходные цвета рисунка сохраняются.
    #
    # Маска используется только как Alpha-канал.
    #
    # Поэтому белые элементы ВНУТРИ рыбки остаются белыми.
    # =========================================================

    rgba = create_rgba(
        cropped_image,
        cropped_mask,
    )

    if rgba is None or rgba.size == 0:
        raise ValueError(
            "Не удалось создать прозрачное изображение."
        )

    if debug_dir is not None:

        cv2.imwrite(
            str(
                debug_dir
                / "13_rgba.png"
            ),
            rgba,
        )

    # =========================================================
    # 7. RESIZE
    # =========================================================

    final_image = resize_rgba(
        rgba,
        max_size=1024,
    )

    if final_image is None or final_image.size == 0:
        raise ValueError(
            "Не удалось изменить размер рыбки."
        )

    if debug_dir is not None:

        cv2.imwrite(
            str(
                debug_dir
                / "14_final.png"
            ),
            final_image,
        )

    # =========================================================
    # 8. ГОТОВО
    # =========================================================

    return final_image
