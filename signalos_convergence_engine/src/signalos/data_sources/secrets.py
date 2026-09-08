from __future__ import annotations

import os


def get_secret(name: str, default: str | None = None) -> str | None:
    """
    Works locally, in GitHub Codespaces, and in Streamlit Cloud.

    Priority:
    1. Environment variable
    2. Streamlit st.secrets, if running inside Streamlit
    3. Default
    """
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st  # type: ignore
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    return default
