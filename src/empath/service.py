"""ChatService — satu-satunya tempat yang mengorkestrasi satu turn."""
from __future__ import annotations

import logging
from collections.abc import Iterator

from empath.config import settings
from empath.llm.client import GeminiClient
from empath.llm.prompts import build_system_prompt
from empath.memory import ConversationMemory
from empath.models import ChatSession, Chunk, Kind, Message, Role
from empath.rag.knowledge import get_knowledge_base
from empath.safety.guard import SafetyGuard

log = logging.getLogger(__name__)

FALLBACK = (
    "Maaf, koneksiku ke model sedang tersendat. Coba kirim lagi ya — "
    "pesanmu tadi tidak hilang."
)


class ChatService:
    def __init__(self, gemini: GeminiClient, guard: SafetyGuard) -> None:
        self._gemini = gemini
        self._guard = guard
        self._memory = ConversationMemory(gemini)
        self._kb = None

    @property
    def kb(self):
        if self._kb is None:
            self._kb = get_knowledge_base()
        return self._kb

    def stream(self, session: ChatSession, user_text: str) -> Iterator[Chunk]:
        verdict = self._guard.inspect(user_text)

        if verdict.blocked:
            session.append(Message(Role.ASSISTANT, verdict.message, kind=Kind.NOTICE))
            yield Chunk("notice", verdict.message)
            yield Chunk("done")
            return

        mark = session.mark()
        session.append(Message(Role.USER, user_text))

        if verdict.crisis:
            yield Chunk("crisis", SafetyGuard.CRISIS_CARD)

        context = self.kb.retrieve(user_text)
        system = build_system_prompt(
            session.persona,
            summary=session.summary,
            context=context,
            crisis=verdict.crisis,
            medical=self._guard.wants_medical_framing(user_text),
        )

        buffer: list[str] = []
        try:
            for token in self._gemini.stream(
                session.contents(settings.history_window), system
            ):
                buffer.append(token)
                yield Chunk("token", token)
        except Exception:
            log.exception("streaming gagal")
            session.rollback(mark)          # buang pesan user yatim
            yield Chunk("error", FALLBACK)
            yield Chunk("done")
            return

        reply = "".join(buffer).strip()
        if not reply:
            session.rollback(mark)
            yield Chunk("error", FALLBACK)
            yield Chunk("done")
            return

        session.append(
            Message(
                Role.ASSISTANT,
                reply,
                kind=Kind.CRISIS if verdict.crisis else Kind.TEXT,
            )
        )
        self._memory.maybe_summarize(session)
        yield Chunk("done", reply)