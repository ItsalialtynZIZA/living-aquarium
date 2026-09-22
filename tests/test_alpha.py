from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

FISH_DIR = (
    BASE_DIR
    / "storage"
    / "fish"
)


for fish_path in FISH_DIR.glob("*.png"):

    image = cv2.imread(
        str(fish_path),
        cv2.IMREAD_UNCHANGED
    )

    print()
    print("=" * 60)
    print("ФАЙЛ:", fish_path.name)

    if image is None:
        print("Ошибка чтения.")
        continue

    alpha = image[:, :, 3]

    total_pixels = alpha.size

    transparent = np.sum(
        alpha == 0
    )

    semi_transparent = np.sum(
        (alpha > 0) &
        (alpha < 255)
    )

    opaque = np.sum(
        alpha == 255
    )

    print(
        "Всего пикселей:",
        total_pixels
    )

    print(
        "Прозрачных:",
        transparent,
        f"({transparent / total_pixels * 100:.2f}%)"
    )

    print(
        "Полупрозрачных:",
        semi_transparent,
        f"({semi_transparent / total_pixels * 100:.2f}%)"
    )

    print(
        "Непрозрачных:",
        opaque,
        f"({opaque / total_pixels * 100:.2f}%)"
    )

    print(
        "Alpha min:",
        alpha.min()
    )

    print(
        "Alpha max:",
        alpha.max()
    )