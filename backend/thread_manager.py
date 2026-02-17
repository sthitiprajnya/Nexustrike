from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PentestThread:
    id: str
    created: datetime
    messages: List[Message] = field(default_factory=list)
    pentest_status: str = "initializing"
    engagement_data: Dict = field(default_factory=dict)


class InMemoryThreadDB:
    def __init__(self) -> None:
        self._threads: Dict[str, PentestThread] = {}

    def save_thread(self, thread: PentestThread) -> None:
        self._threads[thread.id] = thread

    def get_thread(self, thread_id: str) -> Optional[PentestThread]:
        return self._threads.get(thread_id)


class PentestThreadManager:
    def __init__(self, db: Optional[InMemoryThreadDB] = None) -> None:
        self.db = db or InMemoryThreadDB()

    def needs_clarification(self, user_input: str) -> bool:
        return len(user_input.strip().split()) < 2

    def start_autonomous_pentest(self, thread_id: str, user_input: str) -> None:
        thread = self.db.get_thread(thread_id)
        if thread:
            thread.pentest_status = "running"
            thread.engagement_data = {"scope": user_input}

    def create_thread(self, user_input: str) -> PentestThread:
        thread = PentestThread(
            id=str(uuid4()),
            created=datetime.utcnow(),
            messages=[Message(role="user", content=user_input)],
        )
        self.db.save_thread(thread)

        if self.needs_clarification(user_input):
            thread.messages.append(
                Message(
                    role="assistant",
                    content="Please provide target + scope (e.g., domain and depth).",
                )
            )
            return thread

        self.start_autonomous_pentest(thread.id, user_input)
        return thread

    def expand_pentest_scope(self, thread_id: str, user_message: str) -> None:
        thread = self.db.get_thread(thread_id)
        if thread:
            thread.engagement_data["scope_update"] = user_message

    def query_findings(self, thread_id: str, user_message: str) -> Dict:
        thread = self.db.get_thread(thread_id)
        return {"thread_id": thread_id, "query": user_message, "findings": thread.engagement_data.get("findings", []) if thread else []}

    def retest_findings(self, thread_id: str, user_message: str) -> None:
        thread = self.db.get_thread(thread_id)
        if thread:
            thread.engagement_data["retest_request"] = user_message

    def resume_thread(self, thread_id: str, user_message: str):
        thread = self.db.get_thread(thread_id)
        if not thread:
            raise ValueError(f"thread not found: {thread_id}")

        thread.messages.append(Message(role="user", content=user_message))
        msg = user_message.lower()

        if "also" in msg or "scope" in msg:
            self.expand_pentest_scope(thread_id, user_message)
            return {"status": "scope_updated"}
        if "critical" in msg or "findings" in msg:
            return self.query_findings(thread_id, user_message)

        self.retest_findings(thread_id, user_message)
        return {"status": "retest_queued"}
