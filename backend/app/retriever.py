"""
retriever.py — finds the most relevant trusted passages for a question.

WHY THIS FILE EXISTS
--------------------
This is the "R" in RAG (Retrieval-Augmented Generation). Instead of letting the
AI answer from memory (where it can make things up), we first SEARCH our own
library of vetted passages (knowledge/sources.json), then hand the best matches
to the AI and tell it: "answer using these, and cite them."

HOW IT WORKS (BM25, explained simply)
-------------------------------------
BM25 is a classic search-engine scoring formula. For each passage it asks:
  - Does the passage contain the question's words?
  - Are those words rare across the library? (rare words like "utilization"
    are stronger clues than common words like "money")
  - Is the passage extremely long? (long passages get a small penalty so they
    don't win just by having more words)
It's simple, fast, needs no internet, and is a fair baseline. Later you can
upgrade to "embeddings" (meaning-based search) and compare results.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

KNOWLEDGE_FILE = Path(__file__).parent / "knowledge" / "sources.json"

# Very common words that don't help search
_STOPWORDS = {
    "a", "an", "the", "and", "or", "is", "are", "was", "to", "of", "in", "on", "for",
    "it", "i", "my", "me", "you", "your", "do", "does", "what", "how", "can", "should",
    "be", "with", "that", "this", "if", "at", "as", "by", "from", "about", "much", "get",
}


def tokenize(text: str) -> list[str]:
    """Lowercase, split into words, drop stopwords."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS]


@dataclass
class Passage:
    id: str
    title: str
    source: str
    url: str
    text: str


class Retriever:
    def __init__(self, passages: list[Passage], k1: float = 1.5, b: float = 0.75):
        self.passages = passages
        self.k1, self.b = k1, b   # standard BM25 tuning knobs
        # Search over title + text so titles count too
        self.docs = [tokenize(p.title + " " + p.text) for p in passages]
        self.avg_len = sum(len(d) for d in self.docs) / max(len(self.docs), 1)
        # How many passages contain each word (document frequency)
        self.df = Counter(word for doc in self.docs for word in set(doc))
        self.n = len(self.docs)

    @classmethod
    def from_file(cls, path: Path = KNOWLEDGE_FILE) -> "Retriever":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls([Passage(**item) for item in data])

    def _idf(self, word: str) -> float:
        # Rare words get a bigger weight
        df = self.df.get(word, 0)
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 3) -> list[tuple[Passage, float]]:
        q_words = tokenize(query)
        scored = []
        for passage, doc in zip(self.passages, self.docs):
            counts = Counter(doc)
            score = 0.0
            for w in q_words:
                if w not in counts:
                    continue
                tf = counts[w]
                denom = tf + self.k1 * (1 - self.b + self.b * len(doc) / self.avg_len)
                score += self._idf(w) * tf * (self.k1 + 1) / denom
            if score > 0:
                scored.append((passage, round(score, 3)))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
