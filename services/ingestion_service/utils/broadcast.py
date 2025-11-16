import asyncio
from typing import Dict, Set
from fastapi import WebSocket

connections: Dict[str, Set[WebSocket]] = {}
lock = asyncio.Lock()

async def register(ws: WebSocket, symbols):
    async with lock:
        for s in symbols:
            if s not in connections:
                connections[s] = set()
            connections[s].add(ws)
        print(f"Registered WS {id(ws)} to symbols {symbols}", flush=True)

async def unregister(ws: WebSocket):
    async with lock:
        for s, conns in list(connections.items()):
            if ws in conns:
                conns.remove(ws)
                if not conns:
                    connections.pop(s, None)

async def broadcast_update(symbol: str, data: dict):
    async with lock:
        conns = list(connections.get(symbol, set()))
    for ws in conns:
        try:
            await ws.send_json({"symbol": symbol, "data": data})
        except Exception:
            await unregister(ws)