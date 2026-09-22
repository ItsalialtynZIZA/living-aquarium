from pathlib import Path

import cv2
import numpy as np

from app.image_processing.paper_detection import detect_paper
from app.image_processing.perspective import four_point_transform
from app.image_processing.lighting import normalize_lighting


BASE_DIR = Path(__file__).resolve().parent.parent

ORIGINALS_DIR = (
    BASE_DIR
    / "storage"
    / "originals"
)


for image_path in ORIGINALS_DIR.glob("*.jpg"):

    print()
    print("=" * 70)
    print("ФАЙЛ:", image_path.name)

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR
    )

    if image is None:
        continue

    try:

        paper = detect_paper(image)

        if paper is None:
            print("Лист не найден.")
            continue

        warped = four_point_transform(
            image,
            paper
        )

        normalized = normalize_lighting(
            warped
        )

        h, w = normalized.shape[:2]

        # Берём несколько зон,
        # где обычно нет рисунка.
        margin_x = int(w * 0.08)
        margin_y = int(h * 0.08)

        regions = {

            "top_left": normalized[
                0:margin_y,
                0:margin_x
            ],

            "top_right": normalized[
                0:margin_y,
                w-margin_x:w
            ],

            "bottom_left": normalized[
                h-margin_y:h,
                0:margin_x
            ],

            "bottom_right": normalized[
                h-margin_y:h,
                w-margin_x:w
            ],
        }

        print()
        print("ЗОНЫ БУМАГИ:")

        for name, region in regions.items():

            mean_color = np.mean(
                region.reshape(-1, 3),
                axis=0
            )

            median_color = np.median(
                region.reshape(-1, 3),
                axis=0
            )

            print()
            print(name)

            print(
                "mean BGR:",
                np.round(
                    mean_color,
                    1
                )
            )

            print(
                "median BGR:",
                np.round(
                    median_color,
                    1
                )
            )

        # ==========================================
        # ОБЩАЯ СТАТИСТИКА
        # ==========================================

        pixels = normalized.reshape(
            -1,
            3
        )

        mean_color = np.mean(
            pixels,
            axis=0
        )

        median_color = np.median(
            pixels,
            axis=0
        )

        print()
        print("ВСЯ БУМАГА:")

        print(
            "mean BGR:",
            np.round(
                mean_color,
                1
            )
        )

        print(
            "median BGR:",
            np.round(
                median_color,
                1
            )
        )

    except Exception as error:

        print(
            "ОШИБКА:",
            error
        )