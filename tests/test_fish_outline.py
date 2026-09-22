import sys
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.image_processing.fish_outline import detect_fish_outline


input_path = (
    BASE_DIR
    / "storage"
    / "originals"
    / "11ce031c1f33480a8a95ee8c1d642e93.jpg"
)

debug_dir = (
    BASE_DIR
    / "storage"
    / "debug"
    / "outline_test"
)

debug_dir.mkdir(parents=True, exist_ok=True)


image = cv2.imread(str(input_path))

if image is None:
    raise FileNotFoundError(
        f"Не удалось открыть изображение: {input_path}"
    )


mask = detect_fish_outline(image)


output_path = debug_dir / "fish_mask.png"

cv2.imwrite(
    str(output_path),
    mask
)


print("Тест завершён.")
print("Исходник:", input_path)
print("Маска:", output_path)
print("Размер:", mask.shape)

print(
    "Площадь маски:",
    round(
        (mask > 127).mean() * 100,
        2
    ),
    "%"
)