import cv2
import numpy as np


def segment_drawing(
    image: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

    if image is None or image.size == 0:
        raise ValueError("Изображение пустое.")

    height, width = image.shape[:2]

    # ==================================================
    # 1. GRAYSCALE
    # ==================================================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )


    # ==================================================
    # 2. УДАЛЕНИЕ МЕДЛЕННОГО ОСВЕЩЕНИЯ
    # ==================================================

    background = cv2.GaussianBlur(
        gray,
        (0, 0),
        sigmaX=35,
        sigmaY=35
    )

    gray_float = gray.astype(
        np.float32
    )

    background_float = background.astype(
        np.float32
    )

    background_float[
        background_float < 1
    ] = 1

    normalized = (
        gray_float /
        background_float
    ) * 128.0

    normalized = np.clip(
        normalized,
        0,
        255
    ).astype(
        np.uint8
    )


    # ==================================================
    # 3. ЛОКАЛЬНОЕ ОТКЛОНЕНИЕ ОТ БУМАГИ
    # ==================================================

    local_background = cv2.GaussianBlur(
        normalized,
        (0, 0),
        sigmaX=15,
        sigmaY=15
    )

    local_difference = cv2.absdiff(
        normalized,
        local_background
    )


    # ==================================================
    # 4. DARK MASK
    # ==================================================

    dark_mask = np.zeros_like(
        normalized
    )

    dark_mask[
        local_difference > 12
    ] = 255


    # ==================================================
    # 5. ADAPTIVE THRESHOLD
    # ==================================================

    adaptive = cv2.adaptiveThreshold(
        normalized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41,
        8
    )


    # ==================================================
    # 6. CANNY
    # ==================================================

    edges = cv2.Canny(
        normalized,
        30,
        90
    )

    edge_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    edges = cv2.dilate(
        edges,
        edge_kernel,
        iterations=1
    )


    # ==================================================
    # 7. ОБЪЕДИНЕНИЕ
    # ==================================================

    combined = cv2.bitwise_or(
        dark_mask,
        adaptive
    )

    combined = cv2.bitwise_or(
        combined,
        edges
    )


    # ==================================================
    # 8. УДАЛЯЕМ ГРАНИЦУ ЛИСТА
    # ==================================================

    border = max(
        10,
        int(min(height, width) * 0.025)
    )

    combined[
        :border,
        :
    ] = 0

    combined[
        height - border:,
        :
    ] = 0

    combined[
        :,
        :border
    ] = 0

    combined[
        :,
        width - border:
    ] = 0


    # ==================================================
    # 9. MORPHOLOGY
    # ==================================================

    kernel_open = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    combined = cv2.morphologyEx(
        combined,
        cv2.MORPH_OPEN,
        kernel_open
    )

    kernel_close = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    combined = cv2.morphologyEx(
        combined,
        cv2.MORPH_CLOSE,
        kernel_close
    )


    # ==================================================
    # 10. УДАЛЯЕМ МЕЛКИЙ ШУМ
    # ==================================================

    num_labels, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            combined,
            connectivity=8
        )
    )

    cleaned = np.zeros_like(
        combined
    )

    min_area = max(
        30,
        int(height * width * 0.00003)
    )

    for label in range(
        1,
        num_labels
    ):

        area = stats[
            label,
            cv2.CC_STAT_AREA
        ]

        if area >= min_area:

            cleaned[
                labels == label
            ] = 255


    return (
        dark_mask,
        adaptive,
        cleaned
    )