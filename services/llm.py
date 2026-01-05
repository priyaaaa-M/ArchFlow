from __future__ import annotations

import json
from pathlib import Path

from services.llm_provider import ensure_json, get_llm_client


def extract_components_from_text(cleaned_text: str) -> dict:
    root_dir = Path(__file__).resolve().parents[1]
    prompt_path = root_dir / "prompts" / "components_extraction.txt"

    prompt_template = prompt_path.read_text(encoding="utf-8")
    prompt = prompt_template.replace("{CLEANED_TEXT}", cleaned_text)

    client = get_llm_client()
    raw = client.generate_text(prompt)
    payload = ensure_json(raw)
    return json.loads(payload)
