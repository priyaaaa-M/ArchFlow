import re
import json
import ast
from typing import List, Union


class SystemDesignCleaner:

    SYSTEM_KEYWORDS = [
        "system", "architecture", "component", "service",
        "client", "server", "api", "endpoint",
        "load balancer", "gateway", "cdn",
        "cache", "database", "storage",
        "queue", "broker", "worker",
        "replication", "sharding", "partition",
        "consistency", "availability", "latency",
        "throughput", "scalability",
        "model", "pipeline", "training", "inference",
        "monitoring", "logging", "metrics"
    ]

    BOILERPLATE_PATTERNS = [
        r"Article Tags.*",
        r"limited time offer.*",
        r"up to \d+% off.*",
        r"sign in.*sign up",
        r"back to main",
        r"your dashboard",
        r"premium",
        r"pricing",
        r"search⌘k",
        r"watch video.*",
        r"top \d+%",
        r"login to.*",
        r"legal|privacy|terms",
        r"©.*all rights reserved.*",
    ]

    def extract_content(self, data: Union[str, dict]) -> str:
        if isinstance(data, dict):
            return data.get("Content", "") or ""
        return str(data)

    def remove_boilerplate(self, text: str) -> str:
        for p in self.BOILERPLATE_PATTERNS:
            text = re.sub(p, "", text, flags=re.IGNORECASE)
        return text

    def normalize_text(self, text: str) -> str:
        text = text.replace("\ufeff", "")
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def is_relevant(self, sentence: str) -> bool:
        s = sentence.lower()
        return any(k in s for k in self.SYSTEM_KEYWORDS)

    def clean(self, data: Union[str, dict]) -> List[str]:
        raw_text = self.extract_content(data)

        if not raw_text or len(raw_text) < 200:
            return []

        text = self.remove_boilerplate(raw_text)
        text = self.normalize_text(text)

        sentences = re.split(r"(?<=[.!?])\s+", text)

        return [
            s.strip()
            for s in sentences
            if len(s.strip()) > 40 and self.is_relevant(s)
        ]

def parse_scraped_txt(raw_txt: str) -> Union[dict, str]:

    raw_txt = raw_txt.replace("\ufeff", "").strip()

    try:
        return json.loads(raw_txt)
    except Exception:
        pass

    try:
        return ast.literal_eval(raw_txt)
    except Exception:
        pass

    return {"Content": raw_txt}

if __name__ == "__main__":

    with open("Default.txt", "r", encoding="utf-8") as f:
        raw_txt = f.read()

    parsed_input = parse_scraped_txt(raw_txt)


    cleaner = SystemDesignCleaner()
    cleaned = cleaner.clean(parsed_input)

    ans = "\n".join(cleaned)
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(ans)