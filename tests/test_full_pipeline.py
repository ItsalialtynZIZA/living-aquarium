import sys
from pathlib import Path

PROJECT_DIR = Path(r"C:\living-aquarium")
sys.path.insert(0, str(PROJECT_DIR))

import cv2

from app.image_processing.pipeline import process_drawing


TEST_IMAGES = [
    PROJECT_DIR / "storage" / "originals" / "11ce031c1f33480a8a95ee8c1d642e93.jpg",
    PROJECT_DIR / "storage" / "originals" / "detsad-2761050-1675177625.jpg",
]


def test_image(image_path: Path, index: int):
    print()
    print("=" * 60)
    print(f"ТЕСТ {index}")
    print(f"Файл: {image_path.name}")
    print("=" * 60)

    if not image_path.exists():
        print("ОШИБКА: файл не найден.")
        print(f"Путь: {image_path}")
        return

    image = cv2.imread(str(image_path))

    if image is None:
        print("ОШИБКА: OpenCV не смог прочитать изображение.")
        return

    print(f"Исходный размер: {image.shape[1]} x {image.shape[0]}")

    debug_dir = (
        PROJECT_DIR
        / "storage"
        / "debug"
        / f"full_pipeline_{index}"
    )

    try:
        print()
        print("Запускаем полный pipeline...")

        result = process_drawing(
            image,
            debug_dir=debug_dir,
        )

        if result is None:
            print("ОШИБКА: pipeline вернул None.")
            return

        if result.size == 0:
            print("ОШИБКА: pipeline вернул пустое изображение.")
            return

        output_path = (
            PROJECT_DIR
            / "storage"
            / "fish"
            / f"pipeline_test_{index}.png"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        success = cv2.imwrite(
            str(output_path),
            result,
        )

        if not success:
            print("ОШИБКА: не удалось сохранить результат.")
            return

        print()
        print("УСПЕХ")
        print("-" * 60)

        print(
            f"Размер результата: "
            f"{result.shape[1]} x {result.shape[0]}"
        )

        print(f"Каналов: {result.shape[2]}")
        print(f"Тип данных: {result.dtype}")

        if result.shape[2] == 4:
            alpha = result[:, :, 3]

            alpha_pixels = cv2.countNonZero(alpha)

            total_pixels = (
                alpha.shape[0]
                * alpha.shape[1]
            )

            alpha_percent = (
                alpha_pixels
                / total_pixels
                * 100
            )

            print(
                f"Непрозрачная область: "
                f"{alpha_percent:.2f}%"
            )

            print("Alpha-канал: OK")

        else:
            print(
                "ВНИМАНИЕ: изображение не имеет "
                "4-го Alpha-канала."
            )

        print(f"Результат: {output_path}")
        print(f"DEBUG: {debug_dir}")

    except Exception as error:
        print()
        print("ОШИБКА PIPELINE:")
        print("-" * 60)
        print(f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("ТЕСТ ПОЛНОГО PIPELINE")
    print("ЖИВОЙ АКВАРИУМ")
    print("=" * 60)

    for index, image_path in enumerate(
        TEST_IMAGES,
        start=1,
    ):
        test_image(
            image_path,
            index,
        )

    print()
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)