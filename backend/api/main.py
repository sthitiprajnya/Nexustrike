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
        demo_tools = ["recon", "scanner", "enumerator", "validator", "reporter"]
        for idx in range(10):
            await asyncio.sleep(0.2)
            yield {
                "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
                "level": "critical" if idx == 6 else "info",
                "tool": demo_tools[idx % len(demo_tools)],
                "message": f"Thread {thread_id[:8]} step {idx + 1}: simulated execution event",
                "raw_output": "ok",
                "is_vuln": idx == 6,
                "finding": {"title": "Potential SQL injection", "severity": "critical"} if idx == 6 else None,
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
    await asyncio.sleep(0.2)
    memory.set_engagement(
        engagement["thread_id"],
        {
            **engagement,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "findings": [
                {
                    "title": "Simulated weak authentication policy",
                    "severity": "medium",
                }
            ],
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
  <title>Nexustrike // Autonomous Pentest Dashboard</title>
  <style>
    :root {
      --bg: #06090f;
      --bg-2: #0b111d;
      --line: #1a2c3f;
      --text: #cde4ff;
      --muted: #7c95b3;
      --neon: #00ffa3;
      --neon-2: #00b8ff;
      --warn: #ffbc42;
      --crit: #ff3b81;
      --card: rgba(11, 17, 29, 0.88);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      background:
        radial-gradient(circle at 15% 0%, rgba(0, 184, 255, 0.14), transparent 45%),
        radial-gradient(circle at 85% 100%, rgba(0, 255, 163, 0.12), transparent 45%),
        var(--bg);
      min-height: 100vh;
    }
    .topbar {
      height: 56px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      background: rgba(6,9,15,.8);
      backdrop-filter: blur(8px);
      position: sticky;
      top: 0;
      z-index: 9;
    }
    .brand { font-weight: 700; letter-spacing: .5px; }
    .brand span { color: var(--neon); text-shadow: 0 0 10px rgba(0,255,163,.45); }
    .pill {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      color: var(--muted);
      font-size: 12px;
    }
    .layout {
      display: grid;
      grid-template-columns: 280px 1fr 390px;
      gap: 14px;
      padding: 14px;
      height: calc(100vh - 56px);
    }
    .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      overflow: auto;
      box-shadow: 0 0 0 1px rgba(0,184,255,.06) inset;
    }
    .panel h3 {
      margin: 0;
      font-size: 14px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .08em;
      padding: 14px;
      border-bottom: 1px solid var(--line);
    }
    .content { padding: 14px; }
    .thread-item {
      border: 1px solid var(--line);
      padding: 10px;
      border-radius: 10px;
      margin-bottom: 10px;
      color: var(--muted);
      cursor: pointer;
    }
    .thread-item.active { border-color: var(--neon-2); color: var(--text); }
    .label { display:block; font-size:12px; margin-bottom:6px; color:var(--muted); }
    input, textarea, button {
      width: 100%;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: #07101c;
      color: var(--text);
      padding: 10px;
      font: inherit;
    }
    textarea { min-height: 110px; resize: vertical; }
    button {
      margin-top: 10px;
      background: linear-gradient(90deg, var(--neon-2), var(--neon));
      color: #031017;
      border: none;
      font-weight: 700;
      cursor: pointer;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin: 12px 0 14px;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 8px;
      background: #07101c;
    }
    .stat .v { font-size: 18px; color: var(--neon); font-weight: 700; }
    .muted { color: var(--muted); font-size: 12px; }
    #status.running { color: var(--neon); }
    #status.error { color: var(--crit); }
    #logStream { max-height: calc(100vh - 170px); overflow: auto; }
    .log {
      border-bottom: 1px dashed var(--line);
      padding: 8px 0;
      font-size: 12px;
    }
    .log .tool { color: var(--neon-2); }
    .log.critical .tool { color: var(--crit); font-weight: 700; }
    @media (max-width: 1200px) {
      .layout { grid-template-columns: 1fr; height: auto; }
      #logStream { max-height: 350px; }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">NEXU<span>STRIKE</span> // Autonomous Pentest Dashboard</div>
    <div class="pill">Mode: Simulation Scaffold</div>
  </header>

  <section class="layout">
    <aside class="panel">
      <h3>Threads</h3>
      <div class="content">
        <div class="thread-item active" id="activeThreadItem">No active thread</div>
        <div class="thread-item">example.com / full scope</div>
        <div class="thread-item">corp.internal / external perimeter</div>
      </div>
    </aside>

    <main class="panel">
      <h3>Command Center</h3>
      <div class="content">
        <label class="label" for="targetInput">Target / Scope</label>
        <input id="targetInput" placeholder="example.com or 10.10.0.0/24" />

        <label class="label" for="noteInput" style="margin-top:10px;">Operator Intent</label>
        <textarea id="noteInput" placeholder="Pentest target with full coverage, prioritize auth + business logic"></textarea>

        <button id="startBtn">Launch Autonomous Engagement</button>

        <div class="stats">
          <div class="stat"><div class="muted">Status</div><div class="v" id="status">IDLE</div></div>
          <div class="stat"><div class="muted">Tools Run</div><div class="v" id="toolsRun">0</div></div>
          <div class="stat"><div class="muted">Critical</div><div class="v" id="critCount">0</div></div>
        </div>

        <div class="muted">Thread ID: <span id="threadId">not started</span></div>
      </div>
    </main>

    <aside class="panel">
      <h3>🔴 Live Execution Logs</h3>
      <div class="content" id="logStream">
        <div class="muted">No logs yet. Start an engagement to stream events.</div>
      </div>
    </aside>
  </section>

  <script>
    const startBtn = document.getElementById('startBtn');
    const targetInput = document.getElementById('targetInput');
    const threadIdEl = document.getElementById('threadId');
    const statusEl = document.getElementById('status');
    const toolsRunEl = document.getElementById('toolsRun');
    const critCountEl = document.getElementById('critCount');
    const logStream = document.getElementById('logStream');
    const activeThreadItem = document.getElementById('activeThreadItem');

    let toolsRun = 0;
    let critCount = 0;

    function addLog(log) {
      const row = document.createElement('div');
      row.className = 'log ' + (log.level === 'critical' ? 'critical' : '');
      row.innerHTML = `<div><span class="tool">${log.tool}</span> <span class="muted">@ ${log.timestamp}</span></div><div>${log.message}</div>`;
      logStream.prepend(row);

      toolsRun += 1;
      if (log.level === 'critical') critCount += 1;
      toolsRunEl.textContent = toolsRun;
      critCountEl.textContent = critCount;
    }

    async function startEngagement() {
      const target = targetInput.value.trim();
      if (!target) {
        alert('Enter a target first.');
        return;
      }

      statusEl.textContent = 'RUNNING';
      statusEl.className = 'running';
      toolsRun = 0;
      critCount = 0;
      toolsRunEl.textContent = '0';
      critCountEl.textContent = '0';

      const response = await fetch('/api/v1/pentest/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: target,
          authorization_token: 'dev-token'
        })
      });

      if (!response.ok) {
        statusEl.textContent = 'ERROR';
        statusEl.className = 'error';
        return;
      }

      const data = await response.json();
      threadIdEl.textContent = data.thread_id;
      activeThreadItem.textContent = `${target} / ${data.thread_id.slice(0,8)}...`;

      const ws = new WebSocket(`ws://${location.host}/ws/${data.thread_id}`);
      ws.onmessage = (event) => {
        const log = JSON.parse(event.data);
        addLog(log);
      };
      ws.onerror = () => {
        statusEl.textContent = 'ERROR';
        statusEl.className = 'error';
      };
      ws.onclose = () => {
        statusEl.textContent = 'COMPLETED';
      };
    }

    startBtn.addEventListener('click', startEngagement);
  </script>
</body>
</html>
    """


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {"detail": "no favicon"}
