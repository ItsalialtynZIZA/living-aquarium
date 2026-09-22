from fastapi import WebSocket


class ConnectionManager:
    """
    Управляет подключёнными WebSocket-клиентами.

    Сейчас основной клиент — большой экран.
    В дальнейшем сюда можно добавить другие экраны.
    """

    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(
        self,
        websocket: WebSocket
    ):
        """
        Принимает новое WebSocket-соединение.
        """

        await websocket.accept()

        self.connections.append(
            websocket
        )

        print(
            "WebSocket подключён.",
            "Всего подключений:",
            len(self.connections)
        )

    def disconnect(
        self,
        websocket: WebSocket
    ):
        """
        Удаляет отключившийся клиент.
        """

        if websocket in self.connections:

            self.connections.remove(
                websocket
            )

        print(
            "WebSocket отключён.",
            "Всего подключений:",
            len(self.connections)
        )

    async def broadcast(
        self,
        message: dict
    ):
        """
        Отправляет сообщение
        всем подключённым клиентам.
        """

        disconnected = []

        for websocket in self.connections:

            try:

                await websocket.send_json(
                    message
                )

            except Exception:

                disconnected.append(
                    websocket
                )

        for websocket in disconnected:

            self.disconnect(
                websocket
            )


manager = ConnectionManager()