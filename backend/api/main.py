from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.thread_manager import PentestThreadManager


class PentestRequest(BaseModel):
    message: str
    authorization_token: str


class MemoryStore:
    def __init__(self) -> None:
        self._engagements: Dict[str, Dict[str, Any]] = {}

    def set_engagement(self, thread_id: str, engagement: Dict[str, Any]) -> None:
        self._engagements[thread_id] = engagement

    def get_engagement(self, thread_id: str) -> Dict[str, Any]:
        return self._engagements.get(thread_id, {"thread_id": thread_id, "status": "unknown", "findings": []})


class ZeroClawStream:
    async def stream_logs(self, thread_id: str):
        for idx in range(3):
            await asyncio.sleep(0.05)
            yield {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "info",
                "tool": "planner",
                "message": f"Thread {thread_id} heartbeat {idx + 1}",
                "raw_output": "ok",
                "is_vuln": False,
                "finding": None,
            }


app = FastAPI(title="Autonomous Pentest Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

thread_manager = PentestThreadManager()
memory = MemoryStore()
zeroclaw = ZeroClawStream()


async def autonomous_pentest_orchestrator_execute(engagement: Dict[str, Any]) -> None:
    await asyncio.sleep(0.1)
    memory.set_engagement(
        engagement["thread_id"],
        {
            **engagement,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "findings": [],
        },
    )


def parse_scope(user_input: str) -> Dict[str, str]:
    return {"target": user_input.strip(), "scope": "full"}


@app.post("/api/v1/pentest/start")
async def start_pentest(request: PentestRequest):
    thread_id = str(uuid4())
    parsed_scope = parse_scope(request.message)

    engagement = {
        "thread_id": thread_id,
        "target": parsed_scope["target"],
        "scope": parsed_scope["scope"],
        "depth": "thorough",
        "authorization": request.authorization_token,
    }
    memory.set_engagement(thread_id, {**engagement, "status": "started"})
    asyncio.create_task(autonomous_pentest_orchestrator_execute(engagement))

    return {
        "thread_id": thread_id,
        "status": "started",
        "estimated_duration": "8-12 hours",
        "websocket_url": f"ws://localhost:8000/ws/{thread_id}",
    }


@app.websocket("/ws/{thread_id}")
async def websocket_logs(websocket: WebSocket, thread_id: str):
    await websocket.accept()
    try:
        async for log_entry in zeroclaw.stream_logs(thread_id):
            await websocket.send_json(log_entry)
    except WebSocketDisconnect:
        return


@app.get("/api/v1/pentest/{thread_id}/report")
async def get_report(thread_id: str, format: str = "html"):
    engagement_data = memory.get_engagement(thread_id)
    if format == "pdf":
        return {"thread_id": thread_id, "format": "pdf", "content": "PDF generation placeholder"}
    return {"thread_id": thread_id, "format": "html", "content": engagement_data}
