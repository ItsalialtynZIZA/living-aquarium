import os


DEFAULT_DEVICE_CODE = "ASTANA-SCREEN-001"


def get_device_code() -> str:
    device_code = os.getenv(
        "LIVING_AQUARIUM_DEVICE_CODE",
        DEFAULT_DEVICE_CODE,
    )

    device_code = device_code.strip()

    if not device_code:
        raise ValueError(
            "Код устройства не задан."
        )

    return device_code