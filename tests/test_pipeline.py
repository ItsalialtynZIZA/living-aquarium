from pathlib import Path

import cv2

from app.image_processing.pipeline import process_drawing


BASE_DIR = Path(__file__).resolve().parent.parent

ORIGINALS_DIR = (
    BASE_DIR / "storage" / "originals"
)

DEBUG_DIR = (
    BASE_DIR / "storage" / "debug" / "pipeline_test"
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
        print(
            "Фотографии не найдены."
        )
        return

    image_path = files[-1]

    print()
    print("Фотография:")
    print(image_path)

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        print(
            "Не удалось открыть изображение."
        )
        return

    print(
        f"Размер исходного изображения: "
        f"{image.shape[1]} x "
        f"{image.shape[0]}"
    )

    try:

        result = process_drawing(
            image,
            debug_dir=DEBUG_DIR
        )

    except Exception as error:

        print()
        print(
            "ОШИБКА ОБРАБОТКИ:"
        )
        print(error)
        return

    result_path = (
        DEBUG_DIR / "13_final.png"
    )

    print()
    print(
        "PIPELINE УСПЕШНО ЗАВЕРШЁН!"
    )

    print()
    print(
        f"Финальный размер: "
        f"{result.shape[1]} x "
        f"{result.shape[0]}"
    )

    print()
    print(
        f"Финальный файл:"
        f"\n{result_path}"
    )

    print()


if __name__ == "__main__":
    main()