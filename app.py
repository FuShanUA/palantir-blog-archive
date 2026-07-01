import pathlib

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Palantir 博客归档",
    page_icon="📰",
    layout="wide",
)

# Hide Streamlit chrome so the embedded archive fills the viewport.
st.markdown(
    """
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { padding: 0 !important; margin: 0 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .st-emotion-cache-1wmy9hl { gap: 0; }
    iframe { border: none; }
</style>
""",
    unsafe_allow_html=True,
)

HTML_PATH = pathlib.Path(__file__).parent / "index.html"

if not HTML_PATH.exists():
    st.error(f"找不到 index.html：{HTML_PATH}")
    st.stop()

html_content = HTML_PATH.read_text(encoding="utf-8")

components.html(
    html_content,
    height=900,
    scrolling=True,
)
