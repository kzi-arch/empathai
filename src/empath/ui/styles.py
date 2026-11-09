"""CSS. Sedikit saja — Streamlit sudah bagus secara default."""
from __future__ import annotations

import streamlit as st

_CSS = """
<style>
  /* lebar baca yang nyaman untuk percakapan */
  .block-container { max-width: 760px; padding-top: 2.2rem; padding-bottom: 6rem; }

  /* bubble */
  [data-testid="stChatMessage"] {
      border-radius: 16px;
      padding: 0.9rem 1.1rem;
      border: 1px solid rgba(255,255,255,0.06);
  }

  /* kolom feedback menempel di bawah bubble, bukan di samping */
  [data-testid="stChatMessage"] .stButton button,
  [data-testid="stChatMessage"] [data-testid="stFeedback"] { padding: 0.15rem 0.3rem; }

  /* input chat */
  [data-testid="stChatInput"] textarea { border-radius: 14px; }

  /* header hero di empty state */
  .hero { text-align: center; padding: 2.5rem 0 1.5rem; }
  .hero h1 { font-size: 2.1rem; margin-bottom: .35rem; letter-spacing: -.02em; }
  .hero p  { color: #9AA3B8; font-size: .98rem; margin: 0; }

  /* sidebar */
  [data-testid="stSidebar"] .stButton button { text-align: left; }

  /* sembunyikan footer bawaan */
  footer { visibility: hidden; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)