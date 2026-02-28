from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Protocol
from xml.etree import ElementTree

import feedparser
import httpx


@dataclass
class SourceDocument:
    source: str
    source_id: str
    title: str
    authors: str
    abstract: str
    full_text: str
    published_at: datetime
    updated_at: Optional[datetime]
    source_url: str
    arxiv_id: Optional[str] = None


class SourceConnector(Protocol):
    def fetch(self, max_items: int = 100) -> list[SourceDocument]:
        ...


def _request_with_retry(url: str, timeout: int = 60, retries: int = 3) -> httpx.Response:
    headers = {"User-Agent": "aifrontierpulse/0.1 (+https://github.com/karthikabinav/frontier-pulse)"}
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
                response = client.get(url)
                response.raise_for_status()
                return response
        except Exception as exc:  # pragma: no cover - network branch
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2**attempt)
    raise RuntimeError(f"Failed after retries: {url}") from last_error


class ArxivConnector:
    namespace = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

    def __init__(self, categories: list[str]) -> None:
        self.categories = categories

    def fetch(self, max_items: int = 100) -> list[SourceDocument]:
        query = "+OR+".join([f"cat:{cat}" for cat in self.categories])
        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query={query}&sortBy=lastUpdatedDate&sortOrder=descending&start=0&max_results={max_items}"
        )
        response = _request_with_retry(url)
        root = ElementTree.fromstring(response.text)
        docs: list[SourceDocument] = []

        for entry in root.findall("atom:entry", self.namespace):
            title = (entry.findtext("atom:title", default="", namespaces=self.namespace) or "").strip()
            abstract = (entry.findtext("atom:summary", default="", namespaces=self.namespace) or "").strip()
            entry_id = (entry.findtext("atom:id", default="", namespaces=self.namespace) or "").strip()
            published = (entry.findtext("atom:published", default="", namespaces=self.namespace) or "").strip()
            updated = (entry.findtext("atom:updated", default="", namespaces=self.namespace) or "").strip()

            authors = []
            for author_node in entry.findall("atom:author", self.namespace):
                name = author_node.findtext("atom:name", default="", namespaces=self.namespace)
                if name:
                    authors.append(name.strip())

            pdf_url = ""
            for link in entry.findall("atom:link", self.namespace):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href", "")

            docs.append(
                SourceDocument(
                    source="arxiv",
                    source_id=entry_id,
                    title=title,
                    authors=", ".join(authors),
                    abstract=abstract,
                    full_text=f"{title}\n\n{abstract}",
                    published_at=datetime.fromisoformat(published.replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(updated.replace("Z", "+00:00")) if updated else None,
                    source_url=pdf_url or entry_id,
                    arxiv_id=entry_id.split("/")[-1],
                )
            )
        return docs


class RSSConnector:
    def __init__(self, source: str, urls: list[str]) -> None:
        self.source = source
        self.urls = urls

    def fetch(self, max_items: int = 100) -> list[SourceDocument]:
        docs: list[SourceDocument] = []
        for url in self.urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                title = getattr(entry, "title", "").strip()
                summary = getattr(entry, "summary", "").strip()
                link = getattr(entry, "link", "")
                published_parsed = getattr(entry, "published_parsed", None)
                published = datetime(*published_parsed[:6], tzinfo=timezone.utc) if published_parsed else datetime.now(timezone.utc)
                source_id = f"{self.source}:{link or title}"
                docs.append(
                    SourceDocument(
                        source=self.source,
                        source_id=source_id,
                        title=title,
                        authors="",
                        abstract=summary[:3000],
                        full_text=f"{title}\n\n{summary}",
                        published_at=published,
                        updated_at=None,
                        source_url=link,
                    )
                )
                if len(docs) >= max_items:
                    return docs
        return docs


class OpenReviewConnector:
    def __init__(self, venue_id: str = "ICLR.cc/2026/Conference") -> None:
        self.venue_id = venue_id

    def fetch(self, max_items: int = 100) -> list[SourceDocument]:
        url = f"https://api2.openreview.net/notes?content.venueid={self.venue_id}&limit={max_items}"
        response = _request_with_retry(url)
        data = response.json()
        notes = data.get("notes", [])
        docs: list[SourceDocument] = []
        for note in notes[:max_items]:
            content = note.get("content", {})
            title = content.get("title", {}).get("value", "") if isinstance(content.get("title"), dict) else content.get("title", "")
            abstract = content.get("abstract", {}).get("value", "") if isinstance(content.get("abstract"), dict) else content.get("abstract", "")
            note_id = note.get("id", "")
            docs.append(
                SourceDocument(
                    source="openreview",
                    source_id=f"openreview:{note_id}",
                    title=title,
                    authors=", ".join(note.get("writers", [])),
                    abstract=abstract,
                    full_text=f"{title}\n\n{abstract}",
                    published_at=datetime.now(timezone.utc),
                    updated_at=None,
                    source_url=f"https://openreview.net/forum?id={note_id}",
                )
            )
        return docs


def default_rss_sources() -> dict[str, list[str]]:
    return {
        "frontier_blogs": [
            "https://www.anthropic.com/news/rss.xml",
            "https://openai.com/news/rss.xml",
            "https://www.deepmind.com/blog/rss.xml",
        ],
        "reddit": [
            "https://www.reddit.com/r/MachineLearning/.rss",
            "https://www.reddit.com/r/LocalLLaMA/.rss",
        ],
        "university_blogs": [
            "https://bair.berkeley.edu/blog/feed.xml",
            "https://news.mit.edu/rss/topic/artificial-intelligence2",
        ],
        # X official API needs auth; keep this extensible for future connector.
        "x_threads": [],
    }
