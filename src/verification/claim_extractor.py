from __future__ import annotations

import os
import json
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from .config import VerificationConfig


load_dotenv()


CLAIM_EXTRACTION_PROMPT = """
You are extracting factual claims from a technical answer.

Extract only factual statements.

Rules:
- Extract only factual statements.
- Split combined factual statements into atomic claims.
- Do not add knowledge.
- Do not rewrite facts.
- Do not include citations as separate claims.
- Do not include questions or opinions.

Return ONLY valid JSON in this exact structure:

{
  "claims": [
    "claim 1",
    "claim 2"
  ]
}

The response MUST be valid JSON.
"""

class ClaimExtractor:

    def __init__(
        self,
        config: VerificationConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else VerificationConfig()
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

    def extract(
        self,
        answer: str,
    ) -> list[str]:
        schema = {
            "type": "object",
            "properties": {
                "claims": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["claims"],
            "additionalProperties": False,
        }

        def _call(max_tokens: int):
            return self.client.chat.completions.create(
                model=self.config.model,
                temperature=0.0,
                max_completion_tokens=max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": CLAIM_EXTRACTION_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": answer,
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "claim_extraction",
                        "strict": True,
                        "schema": schema,
                    },
                },
            )

        try:
            response = _call(800)
        except Exception as first_err:
            print("[ClaimExtractor] First attempt failed, retrying with larger token limit.")
            print(f"[ClaimExtractor] {first_err}")
            try:
                response = _call(1200)
            except Exception as second_err:
                print("[ClaimExtractor] Retry failed — returning no claims.")
                print(f"[ClaimExtractor] {second_err}")
                return []

        raw = (
            response
            .choices[0]
            .message
            .content
        )

        if not raw:
            return []

        data = json.loads(raw)

        claims = data.get("claims", [])

        if not isinstance(claims, list):
            return []

        return [
            str(claim).strip()
            for claim in claims[: self.config.max_claims]
            if str(claim).strip()
        ]