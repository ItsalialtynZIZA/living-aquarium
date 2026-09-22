from pathlib import Path

import cv2
import numpy as np

from app.image_processing.lighting import normalize_lighting
from app.image_processing.segmentation import segment_drawing
from app.image_processing.cleanup import clean_mask
from app.image_processing.paper_detection import detect_paper
from app.image_processing.perspective import four_point_transform


BASE_DIR = Path(__file__).resolve().parent.parent

FISH_DIR = (
    BASE_DIR
    / "storage"
    / "originals"
)


DEBUG_DIR = (
    BASE_DIR
    / "storage"
    / "debug"
    / "mask_test"
)

DEBUG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


for image_path in FISH_DIR.glob("*"):

    print()
    print("=" * 60)
    print("ФАЙЛ:", image_path.name)

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR
    )

    if image is None:
        print("Не удалось прочитать.")
        continue

    try:

        # ==========================================
        # 1. ЛИСТ
        # ==========================================

        paper = detect_paper(image)

        if paper is None:
            print("Лист не найден.")
            continue


        # ==========================================
        # 2. ПЕРСПЕКТИВА
        # ==========================================

        warped = four_point_transform(
            image,
            paper
        )


        # ==========================================
        # 3. ОСВЕЩЕНИЕ
        # ==========================================

        normalized = normalize_lighting(
            warped
        )


        # ==========================================
        # 4. СЕГМЕНТАЦИЯ
        # ==========================================

        color_mask, dark_mask, combined = (
            segment_drawing(
                normalized
            )
        )


        # ==========================================
        # 5. CLEANUP
        # ==========================================

        cleaned = clean_mask(
            combined
        )


        # ==========================================
        # СТАТИСТИКА
        # ==========================================

        total = cleaned.size

        pixels = np.sum(
            cleaned > 0
        )

        percentage = (
            pixels /
            total *
            100
        )

        print(
            "Размер маски:",
            cleaned.shape
        )

        print(
            "Пикселей рисунка:",
            pixels
        )

        print(
            "Процент маски:",
            round(
                percentage,
                2
            ),
            "%"
        )


        # ==========================================
        # СОХРАНЯЕМ МАСКИ
        # ==========================================

        stem = image_path.stem

        cv2.imwrite(
            str(
                DEBUG_DIR /
                f"{stem}_color.png"
            ),
            color_mask
        )

        cv2.imwrite(
            str(
                DEBUG_DIR /
                f"{stem}_dark.png"
            ),
            dark_mask
        )

        cv2.imwrite(
            str(
                DEBUG_DIR /
                f"{stem}_combined.png"
            ),
            combined
        )

        cv2.imwrite(
            str(
                DEBUG_DIR /
                f"{stem}_cleaned.png"
            ),
            cleaned
        )

        print(
            "Маски сохранены."
        )

    except Exception as error:

        print(
            "ОШИБКА:",
            error
        )