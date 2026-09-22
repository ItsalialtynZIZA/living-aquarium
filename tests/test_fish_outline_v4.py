import sys
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(BASE_DIR),
)

from app.image_processing.fish_outline_v4 import (
    detect_fish_outline_v4,
)


INPUTS = [
    (
        "Рыбка 1",
        BASE_DIR
        / "storage"
        / "originals"
        / "11ce031c1f33480a8a95ee8c1d642e93.jpg",
    ),
    (
        "Рыбка 2",
        BASE_DIR
        / "storage"
        / "originals"
        / "detsad-2761050-1675177625.jpg",
    ),
]


OUTPUT_DIR = (
    BASE_DIR
    / "storage"
    / "debug"
    / "outline_v4"
)


def create_preview(
    image: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:

    white = np.full_like(
        image,
        255,
    )

    alpha = (
        mask.astype(np.float32)
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
        image.astype(np.float32)
        * alpha_3
        +
        white.astype(np.float32)
        * (1.0 - alpha_3)
    )

    return np.clip(
        preview,
        0,
        255,
    ).astype(np.uint8)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for index, (name, input_path) in enumerate(
        INPUTS,
        start=1,
    ):

        print()
        print("=" * 60)
        print(
            f"ТЕСТ V4 — {name}"
        )
        print("=" * 60)

        print(
            "Исходник:",
            input_path,
        )

        image = cv2.imread(
            str(input_path)
        )

        if image is None:

            print(
                "ОШИБКА: изображение не найдено."
            )

            continue

        debug_dir = (
            OUTPUT_DIR
            / f"image_{index}"
        )

        try:

            rgba = detect_fish_outline_v4(
                image,
                debug_dir=debug_dir,
            )

        except Exception as error:

            print(
                "ОШИБКА V4:",
                error,
            )

            continue

        mask = rgba[:, :, 3]

        # ----------------------------------------------------
        # RGBA
        # ----------------------------------------------------

        rgba_path = (
            debug_dir
            / "07_rgba.png"
        )

        cv2.imwrite(
            str(rgba_path),
            rgba,
        )

        # ----------------------------------------------------
        # Preview
        # ----------------------------------------------------

        preview = create_preview(
            image,
            mask,
        )

        preview_path = (
            debug_dir
            / "08_preview_white.jpg"
        )

        cv2.imwrite(
            str(preview_path),
            preview,
        )

        # ----------------------------------------------------
        # Статистика
        # ----------------------------------------------------

        coverage = (
            np.count_nonzero(
                mask > 127
            )
            /
            mask.size
            *
            100
        )

        ys, xs = np.where(
            mask > 127
        )

        print()
        print(
            "Результат:"
        )

        print(
            "RGBA:",
            rgba_path,
        )

        print(
            "Preview:",
            preview_path,
        )

        print(
            "Площадь:",
            round(coverage, 2),
            "%",
        )

        if len(xs) > 0:

            print(
                "X:",
                int(xs.min()),
                "->",
                int(xs.max()),
            )

            print(
                "Y:",
                int(ys.min()),
                "->",
                int(ys.max()),
            )

        print()
        print(
            "6 стадий:"
        )

        print(
            "1:",
            debug_dir / "01_v2_mask.png",
        )

        print(
            "2:",
            debug_dir / "02_v3_mask.png",
        )

        print(
            "3:",
            debug_dir / "03_combined.png",
        )

        print(
            "4:",
            debug_dir / "04_contour.jpg",
        )

        print(
            "5:",
            debug_dir / "05_silhouette.png",
        )

        print(
            "6:",
            debug_dir / "06_final.png",
        )

    print()
    print("=" * 60)
    print("ТЕСТ V4 ЗАВЕРШЁН")
    print("=" * 60)


if __name__ == "__main__":
    main()