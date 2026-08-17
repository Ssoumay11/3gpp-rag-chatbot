from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class GenerationConfig:
    model: str = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    )

    temperature: float = float(
        os.getenv(
            "GROQ_TEMPERATURE",
            "0.0",
        )
    )

    max_tokens: int = int(
        os.getenv(
            "GROQ_MAX_TOKENS",
            "1024",
        )
    )

    # Limit evidence passed to the LLM.
    max_evidence_chunks: int = 5

    # Maximum characters per evidence block.
    max_evidence_chars: int = 6000