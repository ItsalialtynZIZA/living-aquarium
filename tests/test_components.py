from pathlib import Path

import cv2
import numpy as np

from app.image_processing.paper_detection import detect_paper
from app.image_processing.perspective import four_point_transform
from app.image_processing.lighting import normalize_lighting
from app.image_processing.segmentation import segment_drawing


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
        print("Не удалось прочитать.")
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

        color_mask, dark_mask, combined = (
            segment_drawing(
                normalized
            )
        )

        # ==========================================
        # CONNECTED COMPONENTS
        # ==========================================

        num_labels, labels, stats, centroids = (
            cv2.connectedComponentsWithStats(
                combined,
                connectivity=8
            )
        )

        components = []

        for label in range(1, num_labels):

            area = stats[
                label,
                cv2.CC_STAT_AREA
            ]

            x = stats[
                label,
                cv2.CC_STAT_LEFT
            ]

            y = stats[
                label,
                cv2.CC_STAT_TOP
            ]

            width = stats[
                label,
                cv2.CC_STAT_WIDTH
            ]

            height = stats[
                label,
                cv2.CC_STAT_HEIGHT
            ]

            components.append(
                (
                    area,
                    x,
                    y,
                    width,
                    height
                )
            )

        components.sort(
            reverse=True
        )

        total_pixels = combined.size

        print()
        print(
            "Всего компонентов:",
            len(components)
        )

        print()
        print(
            "ТОП-15 КОМПОНЕНТОВ:"
        )

        for index, component in enumerate(
            components[:15],
            start=1
        ):

            area, x, y, width, height = (
                component
            )

            percentage = (
                area /
                total_pixels *
                100
            )

            print(
                f"{index:2d}. "
                f"area={area:7d} "
                f"({percentage:6.2f}%) "
                f"x={x:4d} "
                f"y={y:4d} "
                f"w={width:4d} "
                f"h={height:4d}"
            )

    except Exception as error:

        print(
            "ОШИБКА:",
            error
        )