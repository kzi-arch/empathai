"""Komponen render. Tidak ada logika bisnis di sini."""
from __future__ import annotations

import streamlit as st

from empath.models import Message, Role

AVATAR = {Role.USER: "🧑", Role.ASSISTANT: "🌱"}


def render_message(message: Message, *, index: int, on_rate) -> None:
    with st.chat_message(message.role.value, avatar=AVATAR[message.role]):
        st.markdown(message.content)

        if message.role is not Role.ASSISTANT:
            return

        left, right = st.columns([9, 1], vertical_alignment="center")
        with left:
            st.caption(message.ts.strftime("%H:%M"))
        with right:
            rating = st.feedback(
                "thumbs",
                key=f"rate-{message.id}",
                default=message.rating,
            )
            if rating is not None and rating != message.rating:
                message.rating = rating
                on_rate(message, rating)


def render_stream(chunks, *, crisis_container) -> str:
    """Konsumsi Chunk dan gambar. Mengembalikan teks final."""
    placeholder = st.empty()
    buffer = ""

    for chunk in chunks:
        if chunk.kind == "crisis":
            crisis_container.warning(chunk.text, icon="🫂")
            placeholder = st.empty()
        elif chunk.kind == "token":
            buffer += chunk.text
            placeholder.markdown(buffer + "▌")
        elif chunk.kind in ("error", "notice"):
            placeholder.empty()
            st.error(chunk.text) if chunk.kind == "error" else st.info(chunk.text)

    if buffer:
        placeholder.markdown(buffer)
    return buffer


def render_empty_state(on_pick) -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>Halo. Aku di sini.</h1>
          <p>Nggak harus rapi, nggak harus jelas. Mulai dari mana saja.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    examples = [
        "Hari ini berat banget, aku nggak tahu harus mulai dari mana.",
        "Aku capek terus-terusan nyalahin diri sendiri.",
        "Aku cemas soal sesuatu yang belum terjadi.",
    ]
    for prompt in examples:
        if st.button(prompt, use_container_width=True, key=f"ex-{hash(prompt)}"):
            on_pick(prompt)
            st.rerun()


def render_disclaimer() -> None:
    st.caption(
        "EmpathAI bukan pengganti psikolog, psikiater, atau terapis. "
        "Kalau kamu dalam bahaya, hubungi **119 ext. 8** atau **112**."
    )