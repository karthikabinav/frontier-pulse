from __future__ import annotations

import io
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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


def _extract_pdf_text(pdf_bytes: bytes, parser_primary: str = "pymupdf", parser_fallback: str = "pdfminer") -> str:
    def parse_with_pymupdf(data: bytes) -> str:
        import fitz  # pymupdf

        text_parts: list[str] = []
        doc = fitz.open(stream=data, filetype="pdf")
        try:
            for page in doc:
                text_parts.append(page.get_text("text") or "")
        finally:
            doc.close()
        return "\n".join(text_parts)

    def parse_with_pdfminer(data: bytes) -> str:
        from pdfminer.high_level import extract_text

        return extract_text(io.BytesIO(data)) or ""

    parsers = [parser_primary, parser_fallback]
    for parser_name in parsers:
        try:
            if parser_name == "pymupdf":
                text = parse_with_pymupdf(pdf_bytes)
            elif parser_name == "pdfminer":
                text = parse_with_pdfminer(pdf_bytes)
            else:
                continue
            cleaned = text.strip()
            if cleaned:
                return cleaned
        except Exception:
            continue
    return ""


def _extract_arxiv_full_text(pdf_url: str, fallback_text: str, parser_primary: str, parser_fallback: str) -> str:
    if not pdf_url:
        return fallback_text

    try:
        response = _request_with_retry(pdf_url, timeout=90, retries=3)
        full_text = _extract_pdf_text(response.content, parser_primary=parser_primary, parser_fallback=parser_fallback)
        if full_text:
            # Keep reasonable size in DB while preserving substantial context.
            return full_text[:250_000]
    except Exception:
        pass

    return fallback_text


class ArxivConnector:
    namespace = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

    def __init__(
        self,
        categories: list[str],
        parser_primary: str = "pymupdf",
        parser_fallback: str = "pdfminer",
        recent_hours: int = 24,
        auto_expand_on_empty: bool = True,
        expand_hours: int = 96,
        page_size: int = 100,
        include_current_id_month: bool = True,
        id_months_back: int = 0,
        announcement_days: int = 7,
    ) -> None:
        self.categories = categories
        self.parser_primary = parser_primary
        self.parser_fallback = parser_fallback
        self.recent_hours = recent_hours
        self.auto_expand_on_empty = auto_expand_on_empty
        self.expand_hours = max(expand_hours, recent_hours)
        self.page_size = max(25, min(200, page_size))
        self.include_current_id_month = include_current_id_month
        self.id_months_back = max(0, id_months_back)
        self.announcement_days = max(1, announcement_days)

    def _id_month_prefixes(self) -> list[str]:
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month
        out: list[str] = []
        for _ in range(self.id_months_back + 1):
            out.append(f"{year % 100:02d}{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return out

    def fetch(self, max_items: int = 100) -> list[SourceDocument]:
        query = "+OR+".join([f"cat:{cat}" for cat in self.categories])
        docs: list[SourceDocument] = []
        seen_ids: set[str] = set()

        cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, self.recent_hours))
        start = 0
        page_size = min(self.page_size, max(1, max_items))

        # arXiv can have dense daily activity; paginate until we hit cutoff
        # or reach max_items, rather than assuming one page is enough.
        while len(docs) < max_items:
            url = (
                "https://export.arxiv.org/api/query"
                f"?search_query={query}&sortBy=lastUpdatedDate&sortOrder=descending&start={start}&max_results={page_size}"
            )
            response = _request_with_retry(url)
            root = ElementTree.fromstring(response.text)
            entries = root.findall("atom:entry", self.namespace)
            if not entries:
                break

            reached_older_than_cutoff = False
            for entry in entries:
                title = (entry.findtext("atom:title", default="", namespaces=self.namespace) or "").strip()
                abstract = (entry.findtext("atom:summary", default="", namespaces=self.namespace) or "").strip()
                entry_id = (entry.findtext("atom:id", default="", namespaces=self.namespace) or "").strip()
                published = (entry.findtext("atom:published", default="", namespaces=self.namespace) or "").strip()
                updated = (entry.findtext("atom:updated", default="", namespaces=self.namespace) or "").strip()

                if not entry_id or entry_id in seen_ids:
                    continue

                authors = []
                for author_node in entry.findall("atom:author", self.namespace):
                    name = author_node.findtext("atom:name", default="", namespaces=self.namespace)
                    if name:
                        authors.append(name.strip())

                pdf_url = ""
                for link in entry.findall("atom:link", self.namespace):
                    if link.attrib.get("title") == "pdf":
                        pdf_url = link.attrib.get("href", "")

                published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
                updated_at = datetime.fromisoformat(updated.replace("Z", "+00:00")) if updated else published_at
                # arXiv daily freshness should key off updated_at (new + revised papers)
                if updated_at < cutoff:
                    reached_older_than_cutoff = True
                    continue

                fallback_text = f"{title}\n\n{abstract}"
                full_text = _extract_arxiv_full_text(
                    pdf_url,
                    fallback_text,
                    parser_primary=self.parser_primary,
                    parser_fallback=self.parser_fallback,
                )

                docs.append(
                    SourceDocument(
                        source="arxiv",
                        source_id=entry_id,
                        title=title,
                        authors=", ".join(authors),
                        abstract=abstract,
                        full_text=full_text,
                        published_at=published_at,
                        updated_at=updated_at,
                        source_url=pdf_url or entry_id,
                        arxiv_id=entry_id.split("/")[-1],
                    )
                )
                seen_ids.add(entry_id)
                if len(docs) >= max_items:
                    break

            if reached_older_than_cutoff or len(entries) < page_size or len(docs) >= max_items:
                break
            start += page_size

        # Announcement-aware supplement: include current arXiv ID month (e.g., 2603.*)
        # even when updated_at falls outside a strict last-N-hours cutoff.
        if self.include_current_id_month and len(docs) < max_items:
            supplement_cap = max_items
            month_page_size = min(200, max(50, self.page_size))
            for prefix in self._id_month_prefixes():
                month_start = 0
                while len(docs) < supplement_cap:
                    month_url = (
                        "https://export.arxiv.org/api/query"
                        f"?search_query=id:{prefix}.*&sortBy=submittedDate&sortOrder=descending"
                        f"&start={month_start}&max_results={month_page_size}"
                    )
                    month_response = _request_with_retry(month_url)
                    month_root = ElementTree.fromstring(month_response.text)
                    month_entries = month_root.findall("atom:entry", self.namespace)
                    if not month_entries:
                        break

                    for entry in month_entries:
                        title = (entry.findtext("atom:title", default="", namespaces=self.namespace) or "").strip()
                        abstract = (entry.findtext("atom:summary", default="", namespaces=self.namespace) or "").strip()
                        entry_id = (entry.findtext("atom:id", default="", namespaces=self.namespace) or "").strip()
                        published = (entry.findtext("atom:published", default="", namespaces=self.namespace) or "").strip()
                        updated = (entry.findtext("atom:updated", default="", namespaces=self.namespace) or "").strip()

                        if not entry_id or entry_id in seen_ids:
                            continue

                        entry_cats = [c.attrib.get("term", "") for c in entry.findall("atom:category", self.namespace)]
                        if self.categories and not any(cat in self.categories for cat in entry_cats):
                            continue

                        authors = []
                        for author_node in entry.findall("atom:author", self.namespace):
                            name = author_node.findtext("atom:name", default="", namespaces=self.namespace)
                            if name:
                                authors.append(name.strip())

                        pdf_url = ""
                        for link in entry.findall("atom:link", self.namespace):
                            if link.attrib.get("title") == "pdf":
                                pdf_url = link.attrib.get("href", "")

                        published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
                        updated_at = datetime.fromisoformat(updated.replace("Z", "+00:00")) if updated else published_at

                        fallback_text = f"{title}\n\n{abstract}"
                        # Keep announcement-lane cheap: avoid PDF fetch for wide month scans.
                        full_text = fallback_text

                        docs.append(
                            SourceDocument(
                                source="arxiv",
                                source_id=entry_id,
                                title=title,
                                authors=", ".join(authors),
                                abstract=abstract,
                                full_text=full_text,
                                published_at=published_at,
                                updated_at=updated_at,
                                source_url=pdf_url or entry_id,
                                arxiv_id=entry_id.split("/")[-1],
                            )
                        )
                        seen_ids.add(entry_id)
                        if len(docs) >= supplement_cap:
                            break

                    if len(month_entries) < month_page_size or len(docs) >= supplement_cap:
                        break
                    month_start += month_page_size

                if len(docs) >= supplement_cap:
                    break

        # Announcement-window supplement by submittedDate per category.
        supplement_cap = max(max_items, max_items * 4)
        if len(docs) < supplement_cap:
            end = datetime.now(timezone.utc)
            start_dt = end - timedelta(days=self.announcement_days)
            start_str = start_dt.strftime("%Y%m%d%H%M")
            end_str = end.strftime("%Y%m%d%H%M")

            for cat in self.categories:
                if len(docs) >= supplement_cap:
                    break

                ann_start = 0
                ann_page_size = min(200, max(50, self.page_size))
                while len(docs) < supplement_cap:
                    ann_url = (
                        "https://export.arxiv.org/api/query"
                        f"?search_query=cat:{cat}+AND+submittedDate:[{start_str}+TO+{end_str}]"
                        f"&sortBy=submittedDate&sortOrder=descending&start={ann_start}&max_results={ann_page_size}"
                    )
                    ann_response = _request_with_retry(ann_url)
                    ann_root = ElementTree.fromstring(ann_response.text)
                    ann_entries = ann_root.findall("atom:entry", self.namespace)
                    if not ann_entries:
                        break

                    for entry in ann_entries:
                        title = (entry.findtext("atom:title", default="", namespaces=self.namespace) or "").strip()
                        abstract = (entry.findtext("atom:summary", default="", namespaces=self.namespace) or "").strip()
                        entry_id = (entry.findtext("atom:id", default="", namespaces=self.namespace) or "").strip()
                        published = (entry.findtext("atom:published", default="", namespaces=self.namespace) or "").strip()
                        updated = (entry.findtext("atom:updated", default="", namespaces=self.namespace) or "").strip()

                        if not entry_id or entry_id in seen_ids:
                            continue

                        authors = []
                        for author_node in entry.findall("atom:author", self.namespace):
                            name = author_node.findtext("atom:name", default="", namespaces=self.namespace)
                            if name:
                                authors.append(name.strip())

                        pdf_url = ""
                        for link in entry.findall("atom:link", self.namespace):
                            if link.attrib.get("title") == "pdf":
                                pdf_url = link.attrib.get("href", "")

                        published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
                        updated_at = datetime.fromisoformat(updated.replace("Z", "+00:00")) if updated else published_at

                        fallback_text = f"{title}\n\n{abstract}"
                        docs.append(
                            SourceDocument(
                                source="arxiv",
                                source_id=entry_id,
                                title=title,
                                authors=", ".join(authors),
                                abstract=abstract,
                                full_text=fallback_text,
                                published_at=published_at,
                                updated_at=updated_at,
                                source_url=pdf_url or entry_id,
                                arxiv_id=entry_id.split("/")[-1],
                            )
                        )
                        seen_ids.add(entry_id)
                        if len(docs) >= supplement_cap:
                            break

                    if len(ann_entries) < ann_page_size or len(docs) >= supplement_cap:
                        break
                    ann_start += ann_page_size

        if not docs and self.auto_expand_on_empty and self.expand_hours > self.recent_hours:
            expanded = ArxivConnector(
                self.categories,
                parser_primary=self.parser_primary,
                parser_fallback=self.parser_fallback,
                recent_hours=self.expand_hours,
                auto_expand_on_empty=False,
                expand_hours=self.expand_hours,
                page_size=self.page_size,
                include_current_id_month=self.include_current_id_month,
                id_months_back=self.id_months_back,
                announcement_days=self.announcement_days,
            )
            return expanded.fetch(max_items=max_items)

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
