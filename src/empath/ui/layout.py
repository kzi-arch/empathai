"""Halaman utama."""
from __future__ import annotations

import streamlit as st

from empath.config import settings
from empath.models import Message, Role
from empath.ui import state
from empath.ui.components import (
    render_empty_state,
    render_message,
    render_stream,
)
from empath.ui.sidebar import render_sidebar


def _setup_screen() -> None:
    st.markdown("## 🌱 EmpathAI")
    st.write(
        "API key Gemini belum dikonfigurasi. Buat file `.env` di root proyek:\n\n"
        "```\nGEMINI_API_KEY=isi_di_sini\n```\n\n"
        "Atau tempel key-nya di bawah untuk sesi ini saja."
    )
    key = st.text_input("GEMINI_API_KEY", type="password")
    if key:
        st.session_state.api_key = key.strip()
        st.rerun()
    st.caption("Key tidak disimpan ke disk.")


def render_app() -> None:
    if "api_key" not in st.session_state:
        if settings.configured:
            st.session_state.api_key = settings.gemini_api_key
        else:
            _setup_screen()
            return

    render_sidebar()
    session = state.session()

    if not session.messages:
        render_empty_state(on_pick=lambda text: _send(text))
        return

    for index, message in enumerate(session.messages):
        render_message(
            message,
            index=index,
            on_rate=lambda m, r: st.toast("Terima kasih 🤍"),
        )

    prompt = st.chat_input("Ceritakan apa yang kamu rasakan…")
    if prompt:
        _send(prompt)


def _send(text: str) -> None:
    session = state.session()
    session.append(Message(Role.USER, text))

    with st.chat_message("user", avatar="🧑"):
        st.markdown(text)

    with st.chat_message("assistant", avatar="🌱"):
        crisis_box = st.container()
        final = render_stream(
            state.service().stream(session, text),
            crisis_container=crisis_box,
        )
        if final:
            st.caption("baru saja")