import cv2
from pathlib import Path

from app.image_processing.lighting import normalize_lighting


# ==============================================
# ПУТИ
# ==============================================

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG_DIR = (
    BASE_DIR
    / "storage"
    / "debug"
)

DEBUG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================================
# ИСХОДНЫЙ ФАЙЛ
# ==============================================

input_path = (
    DEBUG_DIR
    / "05_warped.jpg"
)


print()
print("Исходный файл:")
print(input_path)


# ==============================================
# ЧИТАЕМ ИЗОБРАЖЕНИЕ
# ==============================================

image = cv2.imread(
    str(input_path)
)


if image is None:

    print()
    print("Не удалось открыть изображение.")

    raise SystemExit


height, width = image.shape[:2]

print()
print(
    f"Размер изображения: "
    f"{width} x {height}"
)


# ==============================================
# НОРМАЛИЗАЦИЯ
# ==============================================

normalized = normalize_lighting(
    image
)


# ==============================================
# СОХРАНЯЕМ РЕЗУЛЬТАТ
# ==============================================

output_path = (
    DEBUG_DIR
    / "06_normalized.jpg"
)


success = cv2.imwrite(
    str(output_path),
    normalized
)


if not success:

    print()
    print("Не удалось сохранить результат.")

    raise SystemExit


print()
print("Освещение нормализовано!")

print()
print("Файл сохранён:")

print(output_path)