"""Long-term memory: the reviewer's investing profile and summaries of past memos.

Stored as a small JSON file (data/memory/store.json, git-ignored). Short-term memory
(the conversation and the paused graph) lives in the LangGraph checkpointer.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from . import config

DEFAULT_PROFILE = {
    "mandate": "growth",  # growth | value | conservative
    "preferred_metrics": ["revenue", "adj_ebitda", "op_cash_flow"],
}
_LOCK = threading.Lock()


class MemoryStore:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or config.MEMORY_PATH)

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"users": {}}

    def _save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_user(self, user_id: str) -> dict:
        with _LOCK:
            user = self._load()["users"].get(user_id, {})
        return {"profile": {**DEFAULT_PROFILE, **user.get("profile", {})}, "memos": user.get("memos", [])}

    def save_profile(self, user_id: str, profile: dict) -> None:
        with _LOCK:
            data = self._load()
            user = data["users"].setdefault(user_id, {})
            user["profile"] = {**DEFAULT_PROFILE, **user.get("profile", {}), **profile}
            self._save(data)

    def add_memo(self, user_id: str, question: str, summary: str, conviction: dict) -> None:
        with _LOCK:
            data = self._load()
            user = data["users"].setdefault(user_id, {})
            memos = user.setdefault("memos", [])
            memos.append({
                "question": question, "summary": summary, "conviction": conviction,
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            })
            user["memos"] = memos[-10:]
            self._save(data)

    def clear(self, user_id: str) -> None:
        with _LOCK:
            data = self._load()
            data["users"].pop(user_id, None)
            self._save(data)
