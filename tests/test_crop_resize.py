from pathlib import Path

import cv2

from app.image_processing.crop_resize import (
    crop_to_content,
    resize_rgba
)


BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG_DIR = (
    BASE_DIR / "storage" / "debug"
)


def main():

    rgba_path = (
        DEBUG_DIR / "11_rgba.png"
    )

    rgba = cv2.imread(
        str(rgba_path),
        cv2.IMREAD_UNCHANGED
    )

    if rgba is None:
        print(
            "Файл 11_rgba.png не найден."
        )
        return

    print()
    print("Исходный RGBA:")

    print(
        f"Размер: "
        f"{rgba.shape[1]} x "
        f"{rgba.shape[0]}"
    )

    # ---------------------------------------------------------
    # Crop
    # ---------------------------------------------------------

    cropped = crop_to_content(
        rgba,
        padding=20
    )

    cropped_path = (
        DEBUG_DIR / "12_cropped.png"
    )

    cv2.imwrite(
        str(cropped_path),
        cropped
    )

    print()
    print("Crop выполнен!")

    print(
        f"Новый размер: "
        f"{cropped.shape[1]} x "
        f"{cropped.shape[0]}"
    )

    print(
        f"Файл:\n{cropped_path}"
    )

    # ---------------------------------------------------------
    # Resize
    # ---------------------------------------------------------

    resized = resize_rgba(
        cropped,
        max_size=1024
    )

    resized_path = (
        DEBUG_DIR / "13_final.png"
    )

    cv2.imwrite(
        str(resized_path),
        resized
    )

    print()
    print("Resize выполнен!")

    print(
        f"Финальный размер: "
        f"{resized.shape[1]} x "
        f"{resized.shape[0]}"
    )

    print(
        f"Файл:\n{resized_path}"
    )

    print()


if __name__ == "__main__":
    main()