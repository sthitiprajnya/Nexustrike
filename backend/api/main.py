from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
        for idx in range(5):
            await asyncio.sleep(0.15)
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


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Autonomous Pentest Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
    .layout { display: grid; grid-template-columns: 260px 1fr 360px; height: 100vh; }
    .panel { border-right: 1px solid #1e293b; padding: 16px; overflow: auto; }
    .panel:last-child { border-right: none; border-left: 1px solid #1e293b; }
    h2 { margin-top: 0; font-size: 18px; }
    .card { background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
    input, button { width: 100%; box-sizing: border-box; padding: 10px; border-radius: 6px; border: 1px solid #334155; margin-top: 8px; }
    input { background: #0b1220; color: #e2e8f0; }
    button { background: #2563eb; color: white; cursor: pointer; }
    .log { font-size: 12px; margin-bottom: 8px; border-bottom: 1px dashed #334155; padding-bottom: 8px; }
    .muted { color: #94a3b8; font-size: 12px; }
    .success { color: #34d399; }
  </style>
</head>
<body>
  <div class="layout">
    <aside class="panel">
      <h2>Threads</h2>
      <div class="card">
        <div class="muted">Create a new pentest engagement</div>
        <input id="targetInput" placeholder="example.com or 10.0.0.0/24" />
        <button id="startBtn">Start Pentest</button>
      </div>
      <div class="card">
        <strong>Current Thread</strong>
        <div id="threadId" class="muted">Not started</div>
      </div>
    </aside>

    <main class="panel">
      <h2>Chat / Command Center</h2>
      <div class="card">
        <p>Enter target scope on the left, then watch live logs on the right.</p>
        <p class="muted">This is scaffold UI wired to backend API + WebSocket stream.</p>
      </div>
      <div class="card">
        <strong>Status:</strong> <span id="status" class="muted">Idle</span>
      </div>
    </main>

    <aside class="panel">
      <h2>🔴 Live Execution Logs</h2>
      <div id="logs" class="card"><div class="muted">No logs yet.</div></div>
    </aside>
  </div>

  <script>
    const startBtn = document.getElementById('startBtn');
    const targetInput = document.getElementById('targetInput');
    const threadIdEl = document.getElementById('threadId');
    const statusEl = document.getElementById('status');
    const logsEl = document.getElementById('logs');

    function addLog(text) {
      const row = document.createElement('div');
      row.className = 'log';
      row.textContent = text;
      logsEl.prepend(row);
    }

    startBtn.addEventListener('click', async () => {
      const target = targetInput.value.trim();
      if (!target) {
        addLog('Please provide a target first.');
        return;
      }

      statusEl.textContent = 'Starting...';

      const res = await fetch('/api/v1/pentest/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: target, authorization_token: 'dev-token' })
      });

      const data = await res.json();
      threadIdEl.textContent = data.thread_id;
      statusEl.innerHTML = '<span class="success">Running</span>';
      addLog('Started thread: ' + data.thread_id);

      const ws = new WebSocket(`ws://${location.host}/ws/${data.thread_id}`);
      ws.onmessage = (event) => {
        const log = JSON.parse(event.data);
        addLog(`[${log.timestamp}] ${log.tool}: ${log.message}`);
      };
      ws.onclose = () => addLog('Log stream closed.');
    });
  </script>
</body>
</html>
    """


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {"detail": "no favicon"}
