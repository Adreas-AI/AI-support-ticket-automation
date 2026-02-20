"""
OpenAI helper functions for ticket analysis.

Returns a dict with:
- priority: low|medium|high
- category: billing|technical|account|other
- summary: short sentence
- suggested_reply: short professional reply
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def analyze_ticket(subject: str, body: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Ensure .env exists in project root and contains OPENAI_API_KEY=..."
        )

    client = OpenAI(api_key=api_key)

    # Structured Outputs (JSON Schema) — πιο αξιόπιστο από “Return ONLY JSON”
    schema = {
        "name": "ticket_analysis",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "category": {"type": "string", "enum": ["billing", "technical", "account", "other"]},
                "summary": {"type": "string"},
                "suggested_reply": {"type": "string"},
            },
            "required": ["priority", "category", "summary", "suggested_reply"],
        },
        "strict": True,
    }

    messages = [
        {
            "role": "system",
            "content": "You are a helpful customer support assistant. Return structured results.",
        },
        {
            "role": "user",
            "content": f"Ticket subject: {subject}\nTicket body: {body}",
        },
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_schema", "json_schema": schema},
        )
        content = resp.choices[0].message.content
        return json.loads(content)
    except Exception:
        # Fallback: JSON mode (valid JSON, λιγότερο strict)
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                *messages,
                {
                    "role": "user",
                    "content": "Return ONLY a valid JSON object with keys: priority, category, summary, suggested_reply.",
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        return json.loads(content)


