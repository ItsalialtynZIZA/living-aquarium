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

        gray = cv2.cvtColor(
            normalized,
            cv2.COLOR_BGR2GRAY
        )

        # Локальный фон
        background = cv2.GaussianBlur(
            gray,
            (0, 0),
            sigmaX=25,
            sigmaY=25
        )

        # Абсолютное отличие от локального фона
        difference = cv2.absdiff(
            gray,
            background
        )

        print()
        print("LOCAL CONTRAST:")

        print(
            "min:",
            int(np.min(difference))
        )

        print(
            "max:",
            int(np.max(difference))
        )

        print(
            "mean:",
            round(
                float(np.mean(difference)),
                2
            )
        )

        print(
            "median:",
            round(
                float(np.median(difference)),
                2
            )
        )

        for threshold in [
            5,
            10,
            15,
            20,
            25,
            30,
            40,
            50
        ]:

            pixels = np.sum(
                difference > threshold
            )

            percentage = (
                pixels /
                difference.size *
                100
            )

            print(
                f">{threshold:2d}:",
                f"{percentage:6.2f}%"
            )

    except Exception as error:

        print(
            "ОШИБКА:",
            error
        )