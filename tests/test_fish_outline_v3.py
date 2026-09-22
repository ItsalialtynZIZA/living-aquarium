import sys
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(BASE_DIR),
)

from app.image_processing.fish_outline_v3 import (
    detect_fish_outline_v3,
)


INPUT_PATH = (
    BASE_DIR
    / "storage"
    / "originals"
    / "detsad-2761050-1675177625.jpg"
)

OUTPUT_DIR = (
    BASE_DIR
    / "storage"
    / "debug"
    / "outline_v3"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


image = cv2.imread(
    str(INPUT_PATH)
)

if image is None:
    raise FileNotFoundError(
        f"Не удалось открыть изображение: {INPUT_PATH}"
    )


mask = detect_fish_outline_v3(
    image
)


# Маска
mask_path = (
    OUTPUT_DIR
    / "01_fish_mask.png"
)

cv2.imwrite(
    str(mask_path),
    mask,
)


# RGBA
rgba = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2BGRA,
)

rgba[:, :, 3] = mask

rgba_path = (
    OUTPUT_DIR
    / "02_fish_rgba.png"
)

cv2.imwrite(
    str(rgba_path),
    rgba,
)


# Preview на белом фоне
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

preview = np.clip(
    preview,
    0,
    255,
).astype(np.uint8)

preview_path = (
    OUTPUT_DIR
    / "03_preview_white.jpg"
)

cv2.imwrite(
    str(preview_path),
    preview
)


coverage = (
    np.count_nonzero(mask > 127)
    / mask.size
    * 100
)

ys, xs = np.where(
    mask > 127
)

print()
print("=" * 50)
print("FISH OUTLINE V3")
print("=" * 50)

print(
    "Исходник:",
    INPUT_PATH
)

print(
    "Маска:",
    mask_path
)

print(
    "RGBA:",
    rgba_path
)

print(
    "Preview:",
    preview_path
)

print(
    "Площадь выделения:",
    round(coverage, 2),
    "%"
)

if len(xs) > 0:
    print(
        "X:",
        int(xs.min()),
        "->",
        int(xs.max())
    )

    print(
        "Y:",
        int(ys.min()),
        "->",
        int(ys.max())
    )

print("=" * 50)