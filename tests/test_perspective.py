import cv2
import numpy as np
from pathlib import Path

from app.image_processing.paper_detection import detect_paper
from app.image_processing.perspective import four_point_transform


# ==============================================
# ПУТИ
# ==============================================

BASE_DIR = Path(__file__).resolve().parent.parent

ORIGINALS_DIR = (
    BASE_DIR
    / "storage"
    / "originals"
)

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
# ИЩЕМ ПОСЛЕДНЮЮ ФОТОГРАФИЮ
# ==============================================

images = list(
    ORIGINALS_DIR.glob("*.jpg")
) + list(
    ORIGINALS_DIR.glob("*.jpeg")
) + list(
    ORIGINALS_DIR.glob("*.png")
) + list(
    ORIGINALS_DIR.glob("*.webp")
)


if not images:
    print("Фотографии не найдены.")

    raise SystemExit


image_path = max(
    images,
    key=lambda path: path.stat().st_mtime
)


print()
print("Фотография:")
print(image_path)


# ==============================================
# ЧИТАЕМ ФОТО
# ==============================================

image = cv2.imread(
    str(image_path)
)


if image is None:
    print("Не удалось открыть фотографию.")

    raise SystemExit


height, width = image.shape[:2]

print()
print(
    f"Размер изображения: "
    f"{width} x {height}"
)


# ==============================================
# ИЩЕМ ЛИСТ
# ==============================================

corners = detect_paper(image)


if corners is None:

    print()
    print("ЛИСТ НЕ НАЙДЕН!")

    raise SystemExit


print()
print("ЛИСТ НАЙДЕН!")


# ==============================================
# ВЫВОДИМ КООРДИНАТЫ
# ==============================================

print()
print("Координаты четырёх углов:")

for index, point in enumerate(
    corners,
    start=1
):

    x, y = point

    print(
        f"Угол {index}: "
        f"x={x:.1f}, y={y:.1f}"
    )


# ==============================================
# ДЕЛАЕМ DEBUG ИЗОБРАЖЕНИЕ
# ==============================================

debug_image = image.copy()

cv2.polylines(
    debug_image,
    [
        corners.astype(
            np.int32
        ).reshape(
            (-1, 1, 2)
        )
    ],
    True,
    (0, 255, 0),
    5
)


debug_path = (
    DEBUG_DIR
    / "04_detected_sheet.jpg"
)


cv2.imwrite(
    str(debug_path),
    debug_image
)


# ==============================================
# ПЕРСПЕКТИВНОЕ ВЫРАВНИВАНИЕ
# ==============================================

warped = four_point_transform(
    image,
    corners
)


# ==============================================
# СОХРАНЯЕМ РЕЗУЛЬТАТ
# ==============================================

warped_path = (
    DEBUG_DIR
    / "05_warped.jpg"
)


cv2.imwrite(
    str(warped_path),
    warped
)


# ==============================================
# ИНФОРМАЦИЯ
# ==============================================

warped_height, warped_width = (
    warped.shape[:2]
)

print()
print("Перспектива исправлена!")

print(
    f"Размер нового изображения: "
    f"{warped_width} x {warped_height}"
)

print()
print("Файл сохранён:")

print(warped_path)