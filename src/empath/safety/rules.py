"""Pola deteksi. Sengaja sempit: hanya yang benar-benar berisiko."""
from __future__ import annotations

# Krisis: niat menyakiti diri. Wajib memakai \\b dan diuji terhadap negasi.
CRISIS_PATTERNS: tuple[str, ...] = (
    r"\bbunuh\s*diri\b",
    r"\b(mau|ingin|pengen)\s*(mat[iy]|mati)\b",
    r"\bakhiri\s*(hidup|semuanya)\b",
    r"\bmengakhiri\s*hidup\b",
    r"\b(tidak|nggak|enggak)\s*(mau|ingin)\s*hidup\b",
    r"\bkill\s+myself\b",
    r"\bend\s+my\s+life\b",
    r"\bsuicid\w*",
    r"\bself[-\s]?harm\b",
    r"\b(melukai|menyakiti)\s*diri\b",
    r"\boverdosis\b",
)

# Jailbreak: hanya meta-bahasa eksplisit. Frasa seperti "bayangkan kamu",
# "roleplay sebagai", "skenario hipotesis" SENGAJA tidak dimasukkan —
# itu kalimat wajar orang bercerita.
JAILBREAK_PATTERNS: tuple[str, ...] = (
    r"\bignore\s+(all\s+)?(previous|prior|above)\s+instructions?\b",
    r"\babaikan\s+(semua\s+)?(instruksi|aturan|perintah)\b",
    r"\bsystem\s*prompt\b",
    r"\bdeveloper\s*mode\b",
    r"\bjailbreak\b",
    r"\btanpa\s+filter\b",
)

# Indikasi permintaan diagnosis klinis — TIDAK memblokir, hanya menambah
# pengingat halus ke system prompt.
MEDICAL_HINTS: tuple[str, ...] = (
    r"\bapa\s*(aku|saya)\s*(punya|mengidap|kena)\b",
    r"\bdiagnos\w*",
    r"\bgangguan\s*(jiwa|mental|kepribadian)\b",
    r"\b(apakah|apa)\s*(aku|saya)\s*(depresi|bipolar|skizofrenia)\b",
    r"\bobat\s*(apa|untuk)\b",
)

NEGATIONS: tuple[str, ...] = (
    "tidak", "nggak", "ngga", "gak", "ga", "enggak", "engga",
    "bukan", "jangan", "tak", "belum", "no", "not", "never", "dont",
)