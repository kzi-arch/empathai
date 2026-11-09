"""Persistensi percakapan. Atomic write, judul disanitasi."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from empath.config import settings
from empath.models import ChatSession, Message, Role

_SAFE = re.compile(r"[^\w\s-]")


def _slug(text: str, limit: int = 40) -> str:
    cleaned = _SAFE.sub("", text).strip().replace(" ", "_")
    return (cleaned or "percakapan")[:limit]


class ChatStore:
    def __init__(self, directory: Path | None = None) -> None:
        self.dir = directory or settings.data_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, session: ChatSession, title: str | None = None) -> Path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        label = _slug(title or f"Curhat {datetime.now():%d %B}")
        path = self.dir / f"{stamp}_{label}.json"

        payload = {
            "title": title or label.replace("_", " "),
            "timestamp": session.created.isoformat(),
            "persona": session.persona,
            "summary": session.summary,
            "messages": [
                {
                    "role": m.role.value,
                    "content": m.content,
                    "kind": m.kind.value,
                    "ts": m.ts.isoformat(),
                    "rating": m.rating,
                }
                for m in session.messages
            ],
        }

        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)          # atomic — tidak pernah setengah tertulis
        return path

    def list(self) -> list[dict]:
        items: list[dict] = []
        for file in sorted(self.dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            items.append(
                {
                    "path": file,
                    "title": data.get("title", file.stem),
                    "timestamp": data.get("timestamp", ""),
                    "count": len(data.get("messages", [])),
                }
            )
        return items

    def load(self, path: Path) -> ChatSession:
        data = json.loads(path.read_text(encoding="utf-8"))
        session = ChatSession(persona=data.get("persona", "empat"), summary=data.get("summary", ""))
        for raw in data.get("messages", []):
            session.append(
                Message(
                    role=Role(raw["role"]),
                    content=raw["content"],
                    kind=raw.get("kind", "text"),
                    rating=raw.get("rating"),
                )
            )
        return session