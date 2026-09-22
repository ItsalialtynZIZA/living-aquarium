import sys
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.image_processing.fish_outline import detect_fish_outline


input_path = (
    BASE_DIR
    / "storage"
    / "originals"
    / "11ce031c1f33480a8a95ee8c1d642e93.jpg"
)

output_dir = (
    BASE_DIR
    / "storage"
    / "debug"
    / "outline_test"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


image = cv2.imread(str(input_path))

if image is None:
    raise FileNotFoundError(
        f"Не удалось открыть изображение: {input_path}"
    )


# Получаем выделение рыбки
mask = detect_fish_outline(image)


# ---------------------------------------------------------
# Создаём RGBA
# ---------------------------------------------------------

rgba = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2BGRA
)

# Сохраняем исходные цвета изображения.
#
# Меняем ТОЛЬКО alpha-канал.
rgba[:, :, 3] = mask


# ---------------------------------------------------------
# Сохраняем результат
# ---------------------------------------------------------

output_path = (
    output_dir
    / "fish_rgba.png"
)

cv2.imwrite(
    str(output_path),
    rgba
)


# ---------------------------------------------------------
# Дополнительно создаём изображение
# для удобной проверки на белом фоне
# ---------------------------------------------------------

white_background = np.full_like(
    image,
    255
)

alpha = mask.astype(np.float32) / 255.0

alpha_3 = np.dstack(
    [alpha, alpha, alpha]
)

preview = (
    image.astype(np.float32) * alpha_3
    +
    white_background.astype(np.float32) * (1 - alpha_3)
)

preview = np.clip(
    preview,
    0,
    255
).astype(np.uint8)

preview_path = (
    output_dir
    / "fish_preview_white.jpg"
)

cv2.imwrite(
    str(preview_path),
    preview
)


print("Тест RGBA завершён.")
print("Исходник:", input_path)
print("Маска:", output_dir / "fish_mask.png")
print("PNG с прозрачностью:", output_path)
print("Предпросмотр:", preview_path)
print(
    "Площадь маски:",
    round(
        (mask > 127).mean() * 100,
        2
    ),
    "%"
)