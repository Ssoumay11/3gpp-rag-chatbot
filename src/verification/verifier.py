from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.retrieval.models import RetrievalResult

from .config import VerificationConfig
from .evidence_formatter import (
    format_verification_evidence,
)
from .prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)
from .schema import (
    VerificationResponse,
)


load_dotenv()


class ClaimVerifier:

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

    

        
    def verify(
        self,
        claims: list[str],
        evidence: list[RetrievalResult],
    ) -> VerificationResponse:

        if not claims:

            return VerificationResponse(
                all_claims_supported=False,
                claims=[],
                overall_explanation=(
                    "No factual claims were extracted."
                ),
            )

        claims = claims[
            : self.config.max_claims
        ]

        claim_text = "\n".join(
            f"{index}. {claim}"
            for index, claim in enumerate(
                claims,
                start=1,
            )
        )

        evidence_text = (
            format_verification_evidence(
                evidence,
                max_chunks=(
                    self.config.max_evidence_chunks
                ),
                max_chars_per_chunk=(
                    self.config.max_evidence_chars
                ),
            )
        )

        user_prompt = (
            USER_PROMPT_TEMPLATE.format(
                claims=claim_text,
                evidence=evidence_text,
            )
        )

        schema = {
            "type": "object",
            "properties": {
                "all_claims_supported": {
                    "type": "boolean",
                },
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim": {
                                "type": "string",
                            },
                            "supported": {
                                "type": "boolean",
                            },
                            "evidence_chunk_ids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "explanation": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "claim",
                            "supported",
                            "evidence_chunk_ids",
                            "explanation",
                        ],
                        "additionalProperties": False,
                    },
                },
               
            },
            "required": [
                "all_claims_supported",
                "claims",
            ],
            "additionalProperties": False,
        }

        try:
            response = self._call_verifier(
                user_prompt,
                schema,
            )
        except Exception as first_error:
            print(
                "[Verifier] First attempt failed."
            )
            print(
                f"[Verifier] {first_error}"
            )
            response = self._call_verifier(
                user_prompt,
                schema,
            )

        raw = (
            response
            .choices[0]
            .message
            .content
        )

        if not raw:
            raise RuntimeError(
                "Verifier returned empty output."
            )

        data = json.loads(
            raw
        )

        result = (
            VerificationResponse.model_validate(
                data
            )
        )

        # Application-level defensive check.
        actual_all_supported = all(
            claim.supported
            and len(
                claim.evidence_chunk_ids
            ) >= (
                self.config
                .minimum_supporting_evidence
            )
            for claim in result.claims
        )

        result.all_claims_supported = (
            actual_all_supported
            and len(result.claims) == len(claims)
        )

        return result


    def _call_verifier(
        self,
        user_prompt: str,
        schema: dict,
    ):
        return self.client.chat.completions.create(
            model=self.config.model,
            temperature=0.0,
            max_completion_tokens=1200,
            messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "3gpp_claim_verification",
                "strict": True,
                "schema": schema,
            },
        },
    )