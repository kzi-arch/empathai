"""Semua akses session_state lewat sini — tidak ada kunci tersebar."""
from __future__ import annotations

import streamlit as st

from empath.llm.client import GeminiClient
from empath.models import ChatSession
from empath.safety.guard import SafetyGuard
from empath.service import ChatService
from empath.storage import ChatStore


@st.cache_resource(show_spinner=False)
def _gemini(api_key: str) -> GeminiClient:
    return GeminiClient(api_key)


@st.cache_resource(show_spinner=False)
def _store() -> ChatStore:
    return ChatStore()


def gemini() -> GeminiClient:
    return _gemini(st.session_state.api_key)


def store() -> ChatStore:
    return _store()


def service() -> ChatService:
    key = f"svc::{st.session_state.api_key[-8:]}"
    if key not in st.session_state:
        st.session_state[key] = ChatService(gemini(), SafetyGuard())
    return st.session_state[key]


def session() -> ChatSession:
    if "chat" not in st.session_state:
        st.session_state.chat = ChatSession()
    return st.session_state.chat


def new_chat() -> None:
    st.session_state.chat = ChatSession(persona=session().persona)


def load_chat(loaded: ChatSession) -> None:
    st.session_state.chat = loaded