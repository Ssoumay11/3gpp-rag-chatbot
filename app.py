# Application entrypoint
from __future__ import annotations

import time
from src.ui_serialization import (
    serialize_source,
)
import streamlit as st
from src.health import check_qdrant
from source_renderer import (
    format_citation,
    format_source,
)
from src.streamlit_resources import (
    load_rag,
)
from src.ui_config import (
    APP_SUBTITLE,
    APP_TITLE,
    DOCUMENTS,
)


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

def get_value(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .source-card {
        padding: 0.8rem 1rem;
        border: 1px solid #e5e7eb;
        border-radius: 0.6rem;
        margin-bottom: 0.6rem;
        background: #fafafa;
    }

    .status-good {
        color: #15803d;
        font-weight: 600;
    }

    .status-bad {
        color: #b91c1c;
        font-weight: 600;
    }

    .small-text {
        font-size: 0.82rem;
        color: #6b7280;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    f'<div class="main-title">{APP_TITLE}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="subtitle">{APP_SUBTITLE}</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("Knowledge Base")

    st.caption(
        "Only the following documents are used as "
        "the authoritative knowledge source."
    )

    for document in DOCUMENTS:

        st.markdown(
            f"**{document['specification']} "
            f"{document['version']}**"
        )

        st.caption(
            document["description"]
        )
        st.subheader("System")

    qdrant_ok, qdrant_message = (
        check_qdrant()
    )

    if qdrant_ok:
        st.success(
            qdrant_message
        )
    else:
        st.error(
            qdrant_message
        )
    st.divider()

    st.subheader("Retrieval")

    st.write(
        "✓ Dense retrieval"
    )

    st.write(
        "✓ BM25 lexical retrieval"
    )

    st.write(
        "✓ Reciprocal Rank Fusion"
    )

    st.write(
        "✓ Cross-encoder reranking"
    )

    st.divider()

    st.subheader("Safety")

    st.write(
        "✓ Evidence sufficiency gate"
    )

    st.write(
        "✓ Citation validation"
    )

    st.write(
        "✓ Claim-level verification"
    )

    st.write(
        "✓ Out-of-corpus refusal"
    )

    st.divider()

    if st.button(
        "Clear conversation",
        width="stretch",
    ):

        st.session_state.messages = []

        st.rerun()

    st.caption(
        "Answers are restricted to the "
        "indexed 3GPP corpus."
    )


# ---------------------------------------------------------
# Display previous messages
# ---------------------------------------------------------

for message in (
    st.session_state.messages
):

    role = message["role"]

    with st.chat_message(role):

        st.markdown(
            message["content"]
        )

        if (
            role == "assistant"
            and message.get("sources")
        ):

            with st.expander(
                "Sources & evidence"
            ):

                for source in message[
                    "sources"
                ]:

                    st.markdown(
                        format_source(
                            source
                        )
                    )

                    st.caption(
                        f"Chunk: "
                        f"{get_value(source, 'chunk_id', 'unknown')}"
                    )

                    preview = (
                        get_value(source, 'text', '')
                        .replace(
                            "\n",
                            " ",
                        )
                    )

                    if len(preview) > 700:
                        preview = (
                            preview[:700]
                            + "..."
                        )

                    st.write(
                        preview
                    )

                    st.divider()

        if (
            role == "assistant"
            and message.get("diagnostics")
        ):

            with st.expander(
                "Retrieval diagnostics"
            ):

                diagnostics = message[
                    "diagnostics"
                ]

                st.write(
                    f"Evidence allowed: "
                    f"{diagnostics['allowed']}"
                )

                st.write(
                    f"Best evidence score: "
                    f"{diagnostics['best_score']:.4f}"
                )

                st.write(
                    f"Strong evidence chunks: "
                    f"{diagnostics['strong_evidence_count']}"
                )

                st.write(
                    f"Citation valid: "
                    f"{diagnostics['citation_valid']}"
                )


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

prompt = st.chat_input(
    "Ask a question about the indexed 3GPP standards..."
)


if prompt:

    # ---------------------------------------------
    # Show user question
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):

        st.markdown(
            prompt
        )

    # ---------------------------------------------
    # Generate answer
    # ---------------------------------------------

    with st.chat_message("assistant"):

        with st.status(
            "Retrieving and verifying evidence...",
            expanded=False,
        ):

            start = time.perf_counter()

            try:

                rag = load_rag()

                result = rag.ask(
                    prompt
                )

                elapsed = (
                    time.perf_counter()
                    - start
                )

            except Exception as exc:

                st.error(
                    "The RAG pipeline could not process "
                    "this request."
                )

                st.exception(exc)

                st.stop()

        # ---------------------------------------------
        # Answer
        # ---------------------------------------------

        st.markdown(
            result.answer.answer
        )

        # ---------------------------------------------
        # Sources
        # ---------------------------------------------

        if result.evidence:

            with st.expander(
                "Sources & evidence"
            ):

                for source in (
                    result.evidence
                ):

                    st.markdown(
                        format_source(
                            source
                        )
                    )

                    st.caption(
                        f"Chunk: "
                        f"{get_value(source, 'chunk_id', 'unknown')}"
                    )

                    preview = (
                        get_value(source, 'text', '')
                        .replace(
                            "\n",
                            " ",
                        )
                    )

                    if len(preview) > 700:

                        preview = (
                            preview[:700]
                            + "..."
                        )

                    st.write(
                        preview
                    )

                    st.divider()

        # ---------------------------------------------
        # Citation list (trusted)
        # ---------------------------------------------

        if result.trusted_citations:

            with st.expander(
                "Citations"
            ):

                for citation in (
                    result.trusted_citations
                ):

                    if (
                        citation.page_start is not None
                        and citation.page_end is not None
                        and citation.page_start != citation.page_end
                    ):
                        pages = (
                            f"Pages "
                            f"{citation.page_start}–"
                            f"{citation.page_end}"
                        )
                    elif citation.page_start is not None:
                        pages = (
                            f"Page {citation.page_start}"
                        )
                    else:
                        pages = "Page unavailable"

                    section = (
                        citation.section
                        or "Section unavailable"
                    )

                    st.write(
                        f"• {citation.specification} "
                        f"{citation.version}, "
                        f"Section {section}, "
                        f"{pages}"
                    )

        # ---------------------------------------------
        # Diagnostics
        # ---------------------------------------------

        with st.expander(
            "Retrieval diagnostics"
        ):

            st.write(
                f"Evidence allowed: "
                f"{result.evidence_decision.allowed}"
            )

            st.write(
                f"Evidence decision: "
                f"{result.evidence_decision.reason}"
            )

            st.write(
                f"Best evidence score: "
                f"{result.evidence_decision.best_score:.4f}"
            )

            st.write(
                f"Strong evidence chunks: "
                f"{result.evidence_decision.strong_evidence_count}"
            )

            st.write(
                f"Citation validation: "
                f"{result.citation_valid}"
            )

            st.write(
                f"Response time: "
                f"{elapsed:.2f}s"
            )

            if result.citation_errors:

                st.error(
                    "Validation details"
                )

                for error in (
                    result.citation_errors
                ):

                    st.write(
                        f"- {error}"
                    )

        # ---------------------------------------------
        # Save conversation state
        # ---------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer.answer,
                "sources": [
                    serialize_source(
                        source
                )
                    for source in result.evidence
                ],
                "diagnostics": {
                    "allowed": (
                        result.evidence_decision.allowed
                    ),
                    "best_score": (
                        result.evidence_decision.best_score
                    ),
                    "strong_evidence_count": (
                        result.evidence_decision
                        .strong_evidence_count
                    ),
                    "citation_valid": (
                        result.citation_valid
                    ),
                },
            }
        )