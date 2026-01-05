from __future__ import annotations

import json
from pathlib import Path

from services.llm_provider import ensure_json, get_llm_client


def get_relevant_urls(topic: str, count: int = 5) -> list[str]:
    root_dir = Path(__file__).resolve().parents[1]
    prompt_path = root_dir / "prompts" / "url_search.txt"
    prompt_template = prompt_path.read_text(encoding="utf-8")
    prompt = (
        prompt_template.replace("{TOPIC}", topic)
        .replace("{COUNT}", str(count))
    )

    client = get_llm_client()
    raw = client.generate_text(prompt)
    payload = json.loads(ensure_json(raw))

    urls = payload.get("urls")
    if not isinstance(urls, list):
        return []

    out: list[str] = []
    for u in urls:
        if isinstance(u, str) and u.strip():
            out.append(u.strip())

    return out
