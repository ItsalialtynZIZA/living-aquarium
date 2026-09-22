from pathlib import Path

import cv2

from app.image_processing.lighting import normalize_lighting
from app.image_processing.segmentation import segment_drawing
from app.image_processing.cleanup import clean_mask
from app.image_processing.rgba import create_rgba

BASE_DIR = Path(__file__).resolve().parent.parent

ORIGINALS_DIR = BASE_DIR / "storage" / "originals"
DEBUG_DIR = BASE_DIR / "storage" / "debug"

DEBUG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def main():

    files = list(
        ORIGINALS_DIR.glob("*.jpg")
    )

    if not files:
        files = list(
            ORIGINALS_DIR.glob("*.jpeg")
        )

    if not files:
        print("Фотографии не найдены.")
        return

    image_path = files[-1]

    print()
    print("Фотография:")
    print(image_path)

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        print("Не удалось открыть изображение.")
        return

    print(
        f"Размер изображения: "
        f"{image.shape[1]} x {image.shape[0]}"
    )

    # ---------------------------------------------------------
    # Используем результат исправления перспективы
    # ---------------------------------------------------------

    warped_path = (
        DEBUG_DIR / "05_warped.jpg"
    )

    warped = cv2.imread(
        str(warped_path)
    )

    if warped is None:
        print(
            "Файл 05_warped.jpg не найден."
        )
        return

    # ---------------------------------------------------------
    # Нормализация освещения
    # ---------------------------------------------------------

    normalized = normalize_lighting(
        warped
    )

    normalized_path = (
        DEBUG_DIR / "06_normalized.jpg"
    )

    cv2.imwrite(
        str(normalized_path),
        normalized
    )

    # ---------------------------------------------------------
    # Сегментация
    # ---------------------------------------------------------

    color_mask, dark_mask, combined = (
        segment_drawing(normalized)
    )

    # ---------------------------------------------------------
    # Очистка маски
    # ---------------------------------------------------------

    cleaned = clean_mask(
        combined
    )

    rgba = create_rgba(
        normalized,
        cleaned
    )
    # ---------------------------------------------------------
    # Пути сохранения
    # ---------------------------------------------------------

    color_path = (
        DEBUG_DIR / "07_color_mask.png"
    )

    dark_path = (
        DEBUG_DIR / "08_dark_mask.png"
    )

    combined_path = (
        DEBUG_DIR / "09_combined_mask.png"
    )

    cleaned_path = (
        DEBUG_DIR / "10_clean_mask.png"
    )

    rgba_path = (
        DEBUG_DIR / "11_rgba.png"
    )
    # ---------------------------------------------------------
    # Сохраняем результаты
    # ---------------------------------------------------------

    cv2.imwrite(
        str(color_path),
        color_mask
    )

    cv2.imwrite(
        str(dark_path),
        dark_mask
    )

    cv2.imwrite(
        str(combined_path),
        combined
    )

    cv2.imwrite(
        str(cleaned_path),
        cleaned
    )

    cv2.imwrite(
        str(rgba_path),
        rgba
    )

    # ---------------------------------------------------------
    # Результат
    # ---------------------------------------------------------

    print()
    print("Сегментация выполнена!")

    print()
    print("Файлы:")

    print(
        f"07_color_mask.png:"
        f"\n{color_path}"
    )

    print(
        f"08_dark_mask.png:"
        f"\n{dark_path}"
    )

    print(
        f"09_combined_mask.png:"
        f"\n{combined_path}"
    )

    print(
        f"10_clean_mask.png:"
        f"\n{cleaned_path}"
    )

    print(
        f"11_rgba.png:"
        f"\n{rgba_path}"
    )
    
    print()


if __name__ == "__main__":
    main()