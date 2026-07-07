import json
import os

import anthropic

from app.models import CompanyType, FreeTextExtraction, FundingStatus, Geography, RevenueBand

MODEL = "claude-sonnet-5"

EXTRACTION_TOOL = {
    "name": "extract_tam_fields",
    "description": "Extract structured TAM scoring fields from a free-text company description.",
    "input_schema": {
        "type": "object",
        "properties": {
            "company_type": {"type": "string", "enum": [e.value for e in CompanyType]},
            "employee_count": {"type": "integer", "minimum": 0},
            "funding_status": {"type": "string", "enum": [e.value for e in FundingStatus]},
            "revenue_band": {"type": "string", "enum": [e.value for e in RevenueBand]},
            "geography": {"type": "string", "enum": [e.value for e in Geography]},
        },
        "required": ["company_type", "employee_count", "funding_status", "geography"],
    },
}

SYSTEM_PROMPT = (
    "You extract company attributes for a TAM (Total Addressable Market) scoring rubric "
    "from a free-text description. Infer the best-fit enum value for each field from the "
    "text. If a field cannot be reasonably inferred, use 'Unknown' where that option exists, "
    "or make a conservative best guess otherwise. Always call the extract_tam_fields tool."
)


class ExtractionError(Exception):
    pass


def extract_fields(text: str) -> FreeTextExtraction:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ExtractionError("ANTHROPIC_API_KEY is not configured on the server")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_tam_fields"},
        messages=[{"role": "user", "content": text}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_tam_fields":
            try:
                return FreeTextExtraction(**block.input)
            except Exception as exc:
                raise ExtractionError(f"Model returned invalid fields: {exc}") from exc

    raise ExtractionError("Model did not return a structured extraction")
