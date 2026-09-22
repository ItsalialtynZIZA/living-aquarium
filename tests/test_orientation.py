from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

FISH_DIR = (
    BASE_DIR
    / "storage"
    / "fish"
)


for fish_path in FISH_DIR.glob("*.png"):

    print()
    print("=" * 60)
    print("ФАЙЛ:", fish_path.name)

    image = cv2.imread(
        str(fish_path),
        cv2.IMREAD_UNCHANGED
    )

    if image is None:
        print("Ошибка чтения.")
        continue

    alpha = image[:, :, 3]

    mask = np.zeros_like(alpha)
    mask[alpha > 50] = 255

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    print("Размер:", image.shape)
    print("Контуров найдено:", len(contours))

    if not contours:
        continue

    contour = max(
        contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(contour)

    x, y, w, h = cv2.boundingRect(
        contour
    )

    print("Площадь контура:", round(area, 2))

    print(
        "Bounding Box:",
        f"x={x}, y={y}, width={w}, height={h}"
    )

    # ==============================================
    # PCA
    # ==============================================

    points = contour.reshape(
        -1,
        2
    ).astype(np.float32)

    mean, eigenvectors, eigenvalues = cv2.PCACompute2(
        points,
        mean=None
    )

    center = mean[0]

    axis = eigenvectors[0]

    angle = np.degrees(
        np.arctan2(
            axis[1],
            axis[0]
        )
    )

    print(
        "Центр:",
        f"x={center[0]:.1f}, y={center[1]:.1f}"
    )

    print(
        "Главная ось:",
        f"x={axis[0]:.3f}, y={axis[1]:.3f}"
    )

    print(
        "Угол:",
        round(angle, 2),
        "градусов"
    )

    print(
        "Собственные значения:",
        eigenvalues.flatten()
    )

    # ==============================================
    # ПРОЕКЦИИ
    # ==============================================

    center = np.array(
        center,
        dtype=np.float32
    )

    projections = np.dot(
        points - center,
        axis
    )

    min_projection = float(
        np.min(projections)
    )

    max_projection = float(
        np.max(projections)
    )

    print(
        "Минимальная проекция:",
        round(min_projection, 2)
    )

    print(
        "Максимальная проекция:",
        round(max_projection, 2)
    )

    print(
        "Длина основной оси:",
        round(
            max_projection -
            min_projection,
            2
        )
    )

    # ==============================================
    # СРАВНЕНИЕ ЛЕВОЙ И ПРАВОЙ ЧАСТИ
    # ==============================================

    axis_coordinate = np.dot(
        points - center,
        axis
    )

    negative_points = points[
        axis_coordinate < 0
    ]

    positive_points = points[
        axis_coordinate > 0
    ]

    print(
        "Точек слева от центра:",
        len(negative_points)
    )

    print(
        "Точек справа от центра:",
        len(positive_points)
    )

    print("=" * 60)