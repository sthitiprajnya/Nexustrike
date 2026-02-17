from __future__ import annotations

import importlib
import json
import sqlite3
import zlib
from pathlib import Path
from typing import Dict, List


class _CompressionAdapter:
    def __init__(self) -> None:
        if importlib.util.find_spec("zstandard") is not None:
            self._zstd = importlib.import_module("zstandard")
            self._use_zstd = True
        else:
            self._zstd = None
            self._use_zstd = False

    def compress(self, payload: bytes) -> bytes:
        if self._use_zstd:
            return self._zstd.compress(payload, level=3)
        return zlib.compress(payload)

    def decompress(self, payload: bytes) -> bytes:
        if self._use_zstd:
            return self._zstd.decompress(payload)
        return zlib.decompress(payload)


class CompressedKnowledgeBase:
    def __init__(self, db_path: str = "memory.db") -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.compressor = _CompressionAdapter()
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cross_engagement_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engagement_id TEXT,
                target_type TEXT,
                tech_stack_hash TEXT,
                compressed_data BLOB,
                embedding TEXT
            )
            """
        )
        self.conn.commit()

    def hash_tech_stack(self, stack: List[str]) -> str:
        return "|".join(sorted(stack))

    def generate_embedding(self, data: Dict) -> str:
        return f"emb:{len(json.dumps(data))}"

    def store_engagement_learning(self, engagement_data: Dict) -> None:
        compressed_learning = {
            "target_fingerprint": engagement_data.get("target", "unknown"),
            "tech_stack": engagement_data.get("tech_stack", []),
            "vulnerability_patterns": engagement_data.get("vulns", []),
            "successful_tools": engagement_data.get("tools_used", []),
            "exploitation_chains": engagement_data.get("exploits", []),
            "timing_insights": engagement_data.get("timeline", []),
            "novel_discoveries": engagement_data.get("novel_techniques", []),
        }
        compressed_bytes = self.compressor.compress(json.dumps(compressed_learning).encode())
        self.conn.execute(
            """
            INSERT INTO cross_engagement_knowledge
            (engagement_id, target_type, tech_stack_hash, compressed_data, embedding)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                engagement_data.get("id", "unknown"),
                engagement_data.get("target_type", "web"),
                self.hash_tech_stack(engagement_data.get("tech_stack", [])),
                compressed_bytes,
                self.generate_embedding(compressed_learning),
            ),
        )
        self.conn.commit()

    def retrieve_relevant_knowledge(self, new_target: Dict) -> List[Dict]:
        cursor = self.conn.execute("SELECT compressed_data FROM cross_engagement_knowledge LIMIT 10")
        rows = cursor.fetchall()
        relevant_knowledge = []
        for row in rows:
            decompressed = self.compressor.decompress(row["compressed_data"])
            relevant_knowledge.append(json.loads(decompressed))
        return relevant_knowledge
