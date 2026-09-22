import sys
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(BASE_DIR),
)

from app.image_processing.fish_outline import detect_fish_outline


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
    / "outline_v2"
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


# ---------------------------------------------------------
# Выделяем рыбку
# ---------------------------------------------------------

mask = detect_fish_outline(
    image
)


# ---------------------------------------------------------
# Сохраняем маску
# ---------------------------------------------------------

mask_path = (
    OUTPUT_DIR
    / "01_fish_mask.png"
)

cv2.imwrite(
    str(mask_path),
    mask,
)


# ---------------------------------------------------------
# Создаём RGBA
#
# ВАЖНО:
# цвета изображения вообще НЕ изменяем.
# Меняем только alpha.
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Создаём удобный preview на белом фоне
# ---------------------------------------------------------

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
    preview,
)


# ---------------------------------------------------------
# Статистика
# ---------------------------------------------------------

coverage = (
    np.count_nonzero(mask > 127)
    /
    mask.size
    *
    100
)

ys, xs = np.where(
    mask > 127
)

if len(xs) > 0:
    x1 = int(xs.min())
    x2 = int(xs.max())
    y1 = int(ys.min())
    y2 = int(ys.max())

    print()
    print("Область рыбки:")
    print(
        f"X: {x1} -> {x2}"
    )
    print(
        f"Y: {y1} -> {y2}"
    )

print()
print("Тест V2 завершён.")
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