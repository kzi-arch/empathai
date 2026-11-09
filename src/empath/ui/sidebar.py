"""Sidebar: 3 grup jelas — Mulai, Riwayat, Pengaturan."""
from __future__ import annotations

import streamlit as st

from empath.llm.prompts import PERSONAS
from empath.ui import state
from empath.ui.components import render_disclaimer


@st.dialog("Ganti persona?")
def _confirm_persona() -> None:
    target = st.session_state.pending_persona
    st.write(
        f"Beralih ke **{PERSONAS[target]['name']}** akan memulai percakapan baru. "
        "Percakapan sekarang akan hilang kecuali kamu menyimpannya dulu."
    )
    col_save, col_ok, col_no = st.columns(3)
    if col_save.button("Simpan dulu"):
        state.store().save(state.session())
        st.session_state.pending_persona = None
        st.rerun()
    if col_ok.button("Ya, ganti", type="primary"):
        st.session_state.chat.persona = target
        st.session_state.chat.reset()
        st.session_state.pending_persona = None
        st.rerun()
    if col_no.button("Batal"):
        st.session_state.pending_persona = None
        st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🌱 EmpathAI")
        st.caption("Teman curhat")

        if st.button("＋ Percakapan baru", use_container_width=True, type="primary"):
            if state.session().messages:
                state.store().save(state.session(), title="Curhat tersimpan otomatis")
            state.new_chat()
            st.rerun()

        st.divider()

        # ── Riwayat ──────────────────────────────────────────
        saved = state.store().list()
        with st.expander(f"🗂 Riwayat ({len(saved)})", expanded=False):
            if not saved:
                st.caption("Belum ada percakapan tersimpan.")
            for item in saved[:20]:
                if st.button(
                    f"{item['title'][:32]} · {item['count']}",
                    key=f"hist-{item['path'].name}",
                    use_container_width=True,
                ):
                    st.session_state.chat = state.store().load(item["path"])
                    st.rerun()

        # ── Persona ──────────────────────────────────────────
        current = state.session().persona
        with st.expander("🎭 Persona", expanded=False):
            for key, persona in PERSONAS.items():
                active = key == current
                if st.button(
                    f"{persona['emoji']} {persona['name']}"
                    + ("  ✓" if active else ""),
                    key=f"persona-{key}",
                    use_container_width=True,
                    disabled=active,
                    help=persona["desc"],
                ):
                    if state.session().messages:
                        st.session_state.pending_persona = key
                    else:
                        st.session_state.chat.persona = key
                    st.rerun()
            st.caption("Ganti persona akan memulai percakapan baru.")

        # ── Unduh ────────────────────────────────────────────
        st.divider()
        session = state.session()
        if session.messages:
            text = "\n\n".join(
                f"{'Kamu' if m.role.value == 'user' else 'EmpathAI'}: {m.content}"
                for m in session.messages
            )
            st.download_button(
                "⬇ Unduh .txt",
                text,
                file_name=f"empathai_{session.created:%Y%m%d}.txt",
                use_container_width=True,
            )
        else:
            st.button("⬇ Unduh .txt", disabled=True, use_container_width=True)

        st.divider()
        render_disclaimer()

    if st.session_state.get("pending_persona"):
        _confirm_persona()