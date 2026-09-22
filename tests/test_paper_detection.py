import cv2
import numpy as np
from pathlib import Path

from app.image_processing.paper_detection import detect_paper

# ==============================================
# ПУТИ
# ==============================================

BASE_DIR = Path(__file__).resolve().parent.parent

ORIGINALS_DIR = BASE_DIR / "storage" / "originals"

DEBUG_DIR = BASE_DIR / "storage" / "debug"

DEBUG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================================
# ИЩЕМ ФОТОГРАФИЮ
# ==============================================

images = []

for extension in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
    images.extend(
        ORIGINALS_DIR.glob(extension)
    )


if not images:
    print("Ошибка: в storage/originals нет фотографий.")
    raise SystemExit


# Берём последнюю фотографию
image_path = max(
    images,
    key=lambda path: path.stat().st_mtime
)


print()
print("Фотография:")
print(image_path)
print()


# ==============================================
# ЗАГРУЖАЕМ ИЗОБРАЖЕНИЕ
# ==============================================

image = cv2.imread(
    str(image_path)
)


if image is None:
    print("Ошибка: OpenCV не смог открыть фотографию.")
    raise SystemExit


print(
    f"Размер изображения: "
    f"{image.shape[1]} x {image.shape[0]}"
)


# ==============================================
# ИЩЕМ ЛИСТ
# ==============================================

corners = detect_paper(image)


if corners is None:

    print()
    print("ЛИСТ НЕ НАЙДЕН.")
    print()

    raise SystemExit


# ==============================================
# ВЫВОДИМ УГЛЫ
# ==============================================

print()
print("ЛИСТ НАЙДЕН!")
print()
print("Координаты четырёх углов:")

for i, point in enumerate(corners, start=1):

    x, y = point

    print(
        f"Угол {i}: x={x}, y={y}"
    )


# ==============================================
# РИСУЕМ КОНТУР НА DEBUG-ФОТО
# ==============================================

debug_image = image.copy()


cv2.polylines(
    debug_image,
    [
        corners.astype(np.int32).reshape((-1, 1, 2))
    ],
    True,
    (0, 255, 0),
    5
)


# Рисуем точки углов

for i, point in enumerate(corners, start=1):

    x, y = point

    cv2.circle(
        debug_image,
        (int(x), int(y)),
        12,
        (0, 0, 255),
        -1
    )

    cv2.putText(
        debug_image,
        str(i),
        (int(x) + 15, int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 0, 0),
        3
    )


# ==============================================
# СОХРАНЯЕМ DEBUG
# ==============================================

output_path = (
    DEBUG_DIR /
    "04_detected_sheet.jpg"
)


cv2.imwrite(
    str(output_path),
    debug_image
)


print()
print("Debug-файл сохранён:")
print(output_path)
print()