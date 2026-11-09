"""Entrypoint Streamlit — hanya bootstrap."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st
from empath.ui.styles import inject_css

from empath.ui.layout import render_app

st.set_page_config(
    page_title="EmpathAI — Teman Curhat",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="expanded",
)
inject_css()
render_app()