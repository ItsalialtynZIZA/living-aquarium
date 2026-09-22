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

        # -----------------------------
        # Лист
        # -----------------------------

        paper = detect_paper(image)

        if paper is None:
            print("Лист не найден.")
            continue

        warped = four_point_transform(
            image,
            paper
        )

        # -----------------------------
        # Нормализация
        # -----------------------------

        normalized = normalize_lighting(
            warped
        )

        # -----------------------------
        # Маски
        # -----------------------------

        color_mask, dark_mask, combined = (
            segment_drawing(
                normalized
            )
        )

        # -----------------------------
        # Статистика яркости
        # -----------------------------

        gray = cv2.cvtColor(
            normalized,
            cv2.COLOR_BGR2GRAY
        )

        print()
        print("ЯРКОСТЬ GRAY:")

        print(
            "min:",
            int(np.min(gray))
        )

        print(
            "max:",
            int(np.max(gray))
        )

        print(
            "mean:",
            round(
                float(np.mean(gray)),
                2
            )
        )

        print(
            "median:",
            round(
                float(np.median(gray)),
                2
            )
        )

        for percentile in [
            1,
            5,
            10,
            25,
            50,
            75,
            90,
            95,
            99
        ]:

            value = np.percentile(
                gray,
                percentile
            )

            print(
                f"{percentile}%:",
                round(
                    float(value),
                    2
                )
            )

        # -----------------------------
        # Статистика насыщенности
        # -----------------------------

        hsv = cv2.cvtColor(
            normalized,
            cv2.COLOR_BGR2HSV
        )

        saturation = hsv[:, :, 1]

        print()
        print("НАСЫЩЕННОСТЬ S:")

        print(
            "min:",
            int(np.min(saturation))
        )

        print(
            "max:",
            int(np.max(saturation))
        )

        print(
            "mean:",
            round(
                float(np.mean(saturation)),
                2
            )
        )

        print(
            "median:",
            round(
                float(np.median(saturation)),
                2
            )
        )

        # -----------------------------
        # Процент каждой маски
        # -----------------------------

        total = combined.size

        color_pixels = np.sum(
            color_mask > 0
        )

        dark_pixels = np.sum(
            dark_mask > 0
        )

        combined_pixels = np.sum(
            combined > 0
        )

        print()
        print("МАСКИ:")

        print(
            "Color mask:",
            round(
                color_pixels / total * 100,
                2
            ),
            "%"
        )

        print(
            "Dark mask:",
            round(
                dark_pixels / total * 100,
                2
            ),
            "%"
        )

        print(
            "Combined:",
            round(
                combined_pixels / total * 100,
                2
            ),
            "%"
        )

    except Exception as error:

        print(
            "ОШИБКА:",
            error
        )