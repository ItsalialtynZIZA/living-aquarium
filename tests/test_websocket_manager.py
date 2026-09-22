from app.websocket_manager import ConnectionManager


def test_manager_starts_empty():

    manager = ConnectionManager()

    assert manager.connections == []

    print("WebSocket Manager работает.")
    print("Подключений:", len(manager.connections))


if __name__ == "__main__":
    test_manager_starts_empty()