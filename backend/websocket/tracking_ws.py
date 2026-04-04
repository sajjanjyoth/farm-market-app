from fastapi import WebSocket

connections = {}

async def connect(websocket: WebSocket, order_id:int):
    await websocket.accept()
    connections[order_id] = websocket