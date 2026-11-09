"""Ringkasan percakapan. Ter-throttle: bukan setiap turn."""
from __future__ import annotations

import logging

from empath.config import settings
from empath.llm.client import GeminiClient
from empath.models import ChatSession, Role

log = logging.getLogger(__name__)

SUMMARY_PROMPT = """Ringkas percakapan berikut dalam 3–5 kalimat, Bahasa Indonesia.
Fokus pada: perasaan user, topik utama, dan hal penting yang sudah dibahas.
Netral, tanpa diagnosis, tanpa saran baru.

{conversation}

Ringkasan:"""


class ConversationMemory:
    def __init__(self, gemini: GeminiClient) -> None:
        self._gemini = gemini

    def maybe_summarize(self, session: ChatSession) -> bool:
        """Ringkas hanya bila sudah lewat `summarize_every` pesan baru.

        Mengembalikan True bila ringkasan diperbarui.
        """
        if not session.needs_summary(settings.summarize_every):
            return False

        lines: list[str] = []
        if session.summary:
            lines.append(f"Ringkasan sebelumnya: {session.summary}")
        for msg in session.messages[-16:]:
            if msg.role is Role.USER:
                lines.append(f"User: {msg.content}")
            else:
                lines.append(f"EmpathAI: {msg.content}")

        try:
            new_summary = self._gemini.complete(
                SUMMARY_PROMPT.format(conversation="\n".join(lines))
            )
        except Exception:
            log.exception("ringkasan gagal dibuat")
            return False

        if new_summary:
            session.summary = new_summary
            session._summarized_at = len(session.messages)
            return True
        return False