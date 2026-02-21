from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    section_name: str
    text: str
    estimated_tokens: int


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def estimate_tokens(text: str) -> int:
    # Fast approximation for V1.
    return max(1, len(text) // 4)


def split_sections(text: str) -> list[tuple[str, str]]:
    headings = ["abstract", "introduction", "method", "approach", "results", "discussion", "conclusion"]
    lower = text.lower()
    points: list[tuple[int, str]] = []
    for heading in headings:
        idx = lower.find(f"\n{heading}")
        if idx != -1:
            points.append((idx, heading))

    if not points:
        return [("main", text)]

    points.sort(key=lambda x: x[0])
    sections: list[tuple[str, str]] = []
    for i, (start, name) in enumerate(points):
        end = points[i + 1][0] if i + 1 < len(points) else len(text)
        chunk = text[start:end].strip()
        if chunk:
            sections.append((name, chunk))
    return sections or [("main", text)]


def make_chunks(text: str, target_tokens: int, overlap_tokens: int) -> list[Chunk]:
    target_chars = max(1200, target_tokens * 4)
    overlap_chars = max(0, overlap_tokens * 4)
    sections = split_sections(text)
    out: list[Chunk] = []

    for section_name, section_text in sections:
        raw = normalize_whitespace(section_text)
        if not raw:
            continue

        start = 0
        length = len(raw)
        while start < length:
            end = min(length, start + target_chars)
            piece = raw[start:end]
            piece_tokens = estimate_tokens(piece)
            out.append(Chunk(section_name=section_name, text=piece, estimated_tokens=piece_tokens))
            if end >= length:
                break
            start = max(start + 1, end - overlap_chars)

    return out


def strip_reference_tail(text: str) -> str:
    markers = ["\nreferences", "\nappendix", "\nbibliography"]
    lower = text.lower()
    cut = len(text)
    for marker in markers:
        idx = lower.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    return text[:cut].strip()
