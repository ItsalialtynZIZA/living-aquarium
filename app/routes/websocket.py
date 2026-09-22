from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket_manager import manager


router = APIRouter()


@router.websocket("/ws/screen")
async def screen_websocket(websocket: WebSocket):

    await manager.connect(websocket)

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(websocket)

    except Exception as error:

        print(
            "Ошибка WebSocket:",
            error
        )

        manager.disconnect(websocket)