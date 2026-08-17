from __future__ import annotations

import streamlit as st

from src.pipeline import ThreeGPPRAG


@st.cache_resource(
    show_spinner="Loading 3GPP RAG system..."
)
def load_rag() -> ThreeGPPRAG:
    """
    Load the complete RAG pipeline once.

    Streamlit reruns the script for interactions, so expensive
    models and connections must be cached.
    """

    return ThreeGPPRAG()