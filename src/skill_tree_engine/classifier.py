from __future__ import annotations

import re
from typing import List, Tuple

# Category taxonomy for skill tree
RULES: List[Tuple[str, List[str]]] = [
    ("ingestion", ["ingest", "extract", "pdf", "ocr", "parser", "document", "manifest", "drive", "blob", "cas"]),
    ("search", ["search", "bm25", "vector", "embedding", "qdrant", "hybrid", "rerank", "index"]),
    ("agent", ["agent", "skill", "mcp", "tool", "workflow", "orchestr", "claw", "openclaw", "swarm"]),
    ("security", ["security", "quarantine", "scan", "auth", "oauth", "secret", "guard", "billing", "governance", "hitl"]),
    ("frontend", ["frontend", "ui", "react", "html", "css", "spa", "dashboard", "vercel", "web"]),
    ("backend", ["api", "fastapi", "server", "queue", "redis", "postgres", "worker", "deploy"]),
    ("android_re", ["android", "smali", "apk", "manifest", "dex", "package", "seekee", "chatgpt", "grok", "invideo"]),
    ("media", ["video", "audio", "image", "ffmpeg", "whisper", "tts", "imagine", "frame"]),
    ("devops", ["docker", "k8s", "ci", "github", "makefile", "pipeline", "monitor", "prometheus"]),
    ("research", ["research", "report", "notes", "analysis", "forensic", "distill"]),
]


def classify(name: str, description: str = "", path: str = "", kind: str = "") -> str:
    blob = f"{name} {description} {path} {kind}".lower()
    scores = []
    for cat, kws in RULES:
        score = sum(1 for k in kws if k in blob)
        if score:
            scores.append((score, cat))
    if not scores:
        return "general"
    scores.sort(reverse=True)
    return scores[0][1]


def tags_from_text(name: str, description: str = "") -> List[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", f"{name} {description}".lower())
    stop = {"the", "and", "for", "with", "from", "this", "that", "skill", "file", "docs"}
    out = []
    seen = set()
    for w in words:
        if w in stop or w in seen:
            continue
        seen.add(w)
        out.append(w)
        if len(out) >= 8:
            break
    return out


def depth_for_kind(kind: str, category: str) -> int:
    k = (kind or "").lower()
    if k in {"product", "root"}:
        return 0
    if k in {"domain", "category"}:
        return 1
    if category in {"security", "devops"}:
        return 2
    if k in {"policy", "test"}:
        return 3
    return 2
