import re
from abc import ABC, abstractmethod


class BaseCleaner(ABC):
    @abstractmethod
    def clean(self, text: str) -> str:
        pass


class GenericBlogCleaner(BaseCleaner):
    """Cleans generic blog noise from scraped text."""

    BOILERPLATE_KEYWORDS = [
        "sign in", "sign up", "dashboard", "learn ml system design",
        "limited time offer", "hello interview premium", "watch video",
        "back to main", "ask me anything", "get premium", "early access"
    ]

    def clean(self, text: str) -> str:
        text = self._remove_emojis(text)
        text = self._remove_urls_emails(text)
        text = self._remove_boilerplate(text)
        text = self._clean_artifacts(text)
        text = self._deduplicate_lines(text)
        text = self._normalize_whitespace(text)
        return text
        
    def _clean_artifacts(self, text: str) -> str:
        text = text.replace("\\n", "\n").replace("nn", "\n").replace(".n","\n").replace(". n",".")
        text = re.sub(r"[\u200b-\u200d\uFEFF]", "", text)
        text = re.sub(r"\?+", "?", text)
        
        return text


    def _remove_emojis(self, text: str) -> str:
        return re.sub(r"[^\w\s.,;!?-]", "", text)

    def _remove_urls_emails(self, text: str) -> str:
        text = re.sub(r"http\S+|www\.\S+", "", text)
        text = re.sub(r"\S+@\S+", "", text)
        return text
       
    def _remove_noise_numbers(self, text: str) -> str:
        text = re.sub(r'\d{4,}', '', text)
        text = re.sub(r'([!?.])\1{1,}', r'\1', text)
        return text
    '''  
    def _remove_boilerplate(self, text: str) -> str:
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            line_lower = line.lower().strip()
            if any(k in line_lower for k in self.BOILERPLATE_KEYWORDS) and len(line_lower) < 50:
                continue
            # skip one-word lines that are likely noise
            if len(line_lower.split()) <= 2 and not any(c.isalnum() for c in line_lower):
                continue
            cleaned.append(line)
        return "\n".join(cleaned)

    '''
    def _remove_boilerplate(self, text: str) -> str:
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            line_lower = line.lower().strip()
            if any(k in line_lower for k in self.BOILERPLATE_KEYWORDS) and len(line_lower) < 50:
                continue
            cleaned.append(line)
        return "\n".join(cleaned)
        
    def _deduplicate_lines(self, text: str) -> str:
        seen = set()
        deduped = []
        for line in text.splitlines():
            if line.strip() and line not in seen:
                deduped.append(line)
                seen.add(line)
        return "\n".join(deduped)

    def _normalize_whitespace(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text) 
        return text.strip()