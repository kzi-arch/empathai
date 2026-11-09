"""Model domain. Semua state percakapan lewat sini."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Kind(str, Enum):
    TEXT = "text"
    CRISIS = "crisis"      # balasan normal + kartu bantuan
    NOTICE = "notice"      # penolakan jailbreak
    ERROR = "error"


class Risk(str, Enum):
    NONE = "none"
    CRISIS = "crisis"
    JAILBREAK = "jailbreak"


@dataclass(slots=True)
class SafetyVerdict:
    risk: Risk = Risk.NONE
    message: str = ""

    @property
    def blocked(self) -> bool:
        return self.risk is Risk.JAILBREAK

    @property
    def crisis(self) -> bool:
        return self.risk is Risk.CRISIS


@dataclass(slots=True)
class Message:
    role: Role
    content: str
    kind: Kind = Kind.TEXT
    ts: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    rating: int | None = None       # 1 = 👍, 0 = 👎


@dataclass
class ChatSession:
    persona: str = "empat"
    summary: str = ""
    messages: list[Message] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    _summarized_at: int = 0

    # ── mutasi ──────────────────────────────────────────────
    def append(self, message: Message) -> Message:
        self.messages.append(message)
        return message

    def mark(self) -> int:
        """Simpan posisi untuk rollback."""
        return len(self.messages)

    def rollback(self, mark: int) -> None:
        del self.messages[mark:]

    def reset(self) -> None:
        self.messages.clear()
        self.summary = ""
        self._summarized_at = 0

    # ── turunan ─────────────────────────────────────────────
    def contents(self, window: int) -> list[dict]:
        """Bentuk `contents` untuk Gemini dari N pesan terakhir.

        Memastikan: (a) hanya pesan teks, (b) dimulai dari user,
        (c) role bergantian (dua pesan sama digabung).
        """
        msgs = [m for m in self.messages if m.kind in (Kind.TEXT, Kind.CRISIS)]
        msgs = msgs[-window:]

        while msgs and msgs[0].role is not Role.USER:
            msgs.pop(0)

        merged: list[Message] = []
        for m in msgs:
            if merged and merged[-1].role is m.role:
                merged[-1].content += "\n\n" + m.content
            else:
                merged.append(Message(m.role, m.content, m.kind))

        return [
            {
                "role": "user" if m.role is Role.USER else "model",
                "parts": [{"text": m.content}],
            }
            for m in merged
        ]

    @property
    def last_user_text(self) -> str | None:
        for m in reversed(self.messages):
            if m.role is Role.USER:
                return m.content
        return None

    @property
    def turn_count(self) -> int:
        return sum(1 for m in self.messages if m.role is Role.USER)

    def needs_summary(self, every: int) -> bool:
        return len(self.messages) - self._summarized_at >= every


@dataclass(slots=True)
class Chunk:
    """Satu potong output dari ChatService ke UI."""
    kind: str          # token | crisis | notice | error | done
    text: str = ""