from __future__ import annotations

import re
from pathlib import Path

from cleaning.clean_text import SystemDesignCleaner, parse_scraped_txt
from crawlers.crawler import genericCrawler
from services.config import settings
from services.converter import generate_diagram_with_diagrams, to_mermaid
from services.llm import extract_components_from_text
from services.search import get_relevant_urls


def _sanitize_filename(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_") or "topic"


def run_workflow(job_id: str, topic: str, urls: list[str] | None = None) -> dict:
    if not urls:
        urls = get_relevant_urls(topic)

    out_dir = Path(settings.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_topic = _sanitize_filename(topic)

    raw_files: list[str] = []
    for i, url in enumerate(urls):
        title_prefix = out_dir / f"{job_id}_{safe_topic}_{i+1}"
        crawler = genericCrawler()
        crawler.extract(link=url, titlez=str(title_prefix), user=None)
        raw_files.append(str(title_prefix) + ".txt")

    cleaner = SystemDesignCleaner()

    cleaned_chunks: list[str] = []
    for fp in raw_files:
        raw_txt = Path(fp).read_text(encoding="utf-8", errors="ignore")
        parsed = parse_scraped_txt(raw_txt)
        sentences = cleaner.clean(parsed)
        if sentences:
            cleaned_chunks.append("\n".join(sentences))

    cleaned_text = "\n\n".join(cleaned_chunks)

    components_json = extract_components_from_text(cleaned_text)
    
    # Generate beautiful PNG diagram using diagrams library
    diagram_paths = generate_diagram_with_diagrams(components_json, job_id)
    png_path = diagram_paths.get("png", "")
    gif_path = diagram_paths.get("gif", "")
    
    # Keep mermaid for backward compatibility
    mermaid = to_mermaid(components_json)

    return {
        "topic": topic,
        "urls": urls,
        "raw_files": raw_files,
        "cleaned_text": cleaned_text,
        "components": components_json,
        "mermaid": mermaid,
        "png_path": png_path,
        "png_url": f"/files/{Path(png_path).name}" if png_path else "",
        "gif_path": gif_path,
        "gif_url": f"/files/{Path(gif_path).name}" if gif_path else ""
    }
