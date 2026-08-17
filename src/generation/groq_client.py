from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from .config import GenerationConfig


load_dotenv()


class GroqGenerator:
    """
    Strict Groq generation layer.

    This class receives only the question and retrieved evidence.
    """

    def __init__(
        self,
        config: GenerationConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else GenerationConfig()
        )

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=api_key
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = (
            self.client.chat.completions.create(
                model=self.config.model,
                temperature=self.config.temperature,
                max_completion_tokens=(
                    self.config.max_tokens
                ),
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                response_format={
                    "type": "json_object"
                },
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        return content