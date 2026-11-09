"""SafetyGuard: klasifikasi pesan user, bukan memblokir emosi."""
from __future__ import annotations

import re
from functools import lru_cache

from empath.models import Risk, SafetyVerdict
from empath.safety import rules

_CLAUSE_BREAK = re.compile(r"[,.;!?]|\b(?:tapi|tetapi|namun|melainkan)\b", re.IGNORECASE)


@lru_cache(maxsize=64)
def _compiled(patterns: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(p, re.IGNORECASE) for p in patterns)


def _negated(text: str, start: int, window: int = 32) -> bool:
    """True bila klausa tepat sebelum match mengandung negasi.

    "aku nggak mau mati"        → negated (kata 'nggak' di klausa sama)
    "aku nggak kuat, mau mati"  → tidak (koma memutus klausa)
    """
    head = text[max(0, start - window):start]
    tail = _CLAUSE_BREAK.split(head)[-1]
    return any(re.search(rf"\b{re.escape(n)}\b", tail, re.IGNORECASE) for n in rules.NEGATIONS)


class SafetyGuard:
    CRISIS_CARD = (
        "**Aku di sini. Kamu tidak sendirian.**\n\n"
        "Kalau yang kamu rasakan sekarang terasa terlalu berat, tolong hubungi:\n\n"
        "- **119 ext. 8** — Kemenkes, layanan kesehatan jiwa 24 jam\n"
        "- **0811-3855-988** — Into The Light Indonesia\n"
        "- **112** — nomor darurat nasional\n\n"
        "Aku akan tetap menemanimu di sini. Tapi kalau ada orang di sekitarmu "
        "yang bisa kamu hubungi sekarang, tolong lakukan."
    )

    JAILBREAK_REPLY = (
        "Aku nggak bisa masuk ke mode itu ya. Tapi aku tetap di sini kok — "
        "kalau ada yang lagi berat, ceritakan saja."
    )

    def inspect(self, message: str) -> SafetyVerdict:
        text = " ".join(message.split())

        if self._matches(text, rules.JAILBREAK_PATTERNS, respect_negation=False):
            return SafetyVerdict(Risk.JAILBREAK, self.JAILBREAK_REPLY)

        if self._matches(text, rules.CRISIS_PATTERNS, respect_negation=True):
            return SafetyVerdict(Risk.CRISIS, self.CRISIS_CARD)

        return SafetyVerdict(Risk.NONE)

    def wants_medical_framing(self, message: str) -> bool:
        text = " ".join(message.split())
        return self._matches(text, rules.MEDICAL_HINTS, respect_negation=True)

    @staticmethod
    def _matches(text: str, patterns: tuple[str, ...], *, respect_negation: bool) -> bool:
        for pattern in _compiled(patterns):
            for match in pattern.finditer(text):
                if respect_negation and _negated(text, match.start()):
                    continue
                return True
        return False