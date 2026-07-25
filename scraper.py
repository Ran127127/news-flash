"""
Auto-News-Hub Scraper
=====================
RSS-first scraping with generic HTML fallback.
"""

import json
import logging
import os
import re
import time
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)

# ── HTTP helpers ────────────────────────────────────────

session = requests.Session()
session.headers.update({
    "User-Agent": config.USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
})


def _fetch(url, as_text=True):
    """Fetch URL with retries and timeout."""
    for attempt in range(config.MAX_RETRIES):
        try:
            resp = session.get(url, timeout=config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            if as_text:
                resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text if as_text else resp.content
        except Exception as e:
            logger.warning("Fetch attempt %d failed for %s: %s", attempt + 1, url, e)
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.REQUEST_DELAY)
    return None


def _make_id(url, title):
    """Generate a stable unique ID for an article."""
    raw = f"{url}|{title}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def _clean_text(text):
    """Strip and normalize text content."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    # Remove trailing ellipsis artifacts
    text = text.strip("... \u2026")
    return text


def _parse_date(date_str):
    """Try to parse a date string into ISO format."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    # feedparser date struct
    if hasattr(date_str, "tm_year"):
        try:
            dt = datetime(*date_str[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            pass
    if isinstance(date_str, str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
        ):
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except ValueError:
                continue
    return datetime.now(timezone.utc).isoformat()


# ── RSS scraper ─────────────────────────────────────────

def _scrape_rss(source):
    """Scrape articles from an RSS feed."""
    feed_url = source["feed_url"]
    logger.info("Fetching RSS: %s", feed_url)
    text = _fetch(feed_url)
    if not text:
        return []

    feed = feedparser.parse(text)
    articles = []
    max_items = source.get("max_items", 15)

    for entry in feed.entries[:max_items]:
        title = _clean_text(entry.get("title", ""))
        link = entry.get("link", "")
        if not title or not link:
            continue

        # Build summary from entry content
        summary = ""
        if entry.get("summary"):
            soup = BeautifulSoup(entry.summary, "html.parser")
            summary = _clean_text(soup.get_text()[:200])
        elif entry.get("description"):
            soup = BeautifulSoup(entry.description, "html.parser")
            summary = _clean_text(soup.get_text()[:200])

        date_str = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            date_str = _parse_date(entry.published_parsed)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            date_str = _parse_date(entry.updated_parsed)

        articles.append({
            "id": _make_id(link, title),
            "title": title,
            "summary": summary[:150] + "..." if len(summary) > 150 else summary,
            "url": link,
            "source": source["name"],
            "base_url": source["base_url"],
            "date": date_str or datetime.now(timezone.utc).isoformat(),
            "image": "",
        })

    logger.info("RSS %s: found %d articles", source["name"], len(articles))
    return articles


# ── HTML scraper ────────────────────────────────────────

def _scrape_html(source):
    """Scrape articles from an HTML page using CSS selectors."""
    url = source["scrape_url"]
    logger.info("Scraping HTML: %s", url)
    html = _fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    selectors = source.get("selectors", {})
    max_items = source.get("max_items", 15)
    articles = []
    seen_urls = set()

    # Strategy 1: Use configured selectors
    link_selector = selectors.get("article_link", "a")
    candidates = soup.select(link_selector)

    if not candidates:
        # Strategy 2: Generic - find all links that look like articles
        candidates = soup.find_all("a", href=True)

    title_selector = selectors.get("title", "h2, h3, h4")
    summary_selector = selectors.get("summary", "p, .desc, .summary")

    for a_tag in candidates:
        if len(articles) >= max_items:
            break

        href = a_tag.get("href", "")
        if not href or href == "#" or href.startswith("javascript:"):
            continue

        # Make absolute URL
        full_url = urljoin(url, href)

        # Skip non-article links
        parsed = urlparse(full_url)
        if parsed.path in ("/", "") or len(parsed.path) < 5:
            continue
        # Skip media/file links
        if any(parsed.path.lower().endswith(ext) for ext in (
            ".jpg", ".png", ".gif", ".mp4", ".pdf", ".zip"
        )):
            continue
        # Skip duplicate URLs
        if full_url in seen_urls:
            continue

        # Try to extract title
        title = ""
        # Check the <a> tag itself
        a_text = _clean_text(a_tag.get_text())
        if len(a_text) > 6:
            title = a_text
        else:
            # Look for title in nearby elements
            parent = a_tag.parent
            if parent:
                for sel in title_selector.split(","):
                    el = parent.select_one(sel.strip())
                    if el:
                        t = _clean_text(el.get_text())
                        if len(t) > 6:
                            title = t
                            break

        if not title or len(title) < 4:
            continue

        # Skip navigation / boilerplate
        skip_words = [
            "\u767b\u5f55", "\u6ce8\u518c", "\u5173\u6ce8", "\u5fae\u4fe1", "\u5fae\u535a",
            "\u4e0b\u8f7d", "APP", "\u5ba2\u6237\u7aef", "\u8054\u7cfb\u6211\u4eec",
            "\u7f51\u7ad9\u5730\u56fe", "\u5173\u4e8e\u6211\u4eec",
        ]
        if any(w in title for w in skip_words):
            continue

        seen_urls.add(full_url)

        # Try to extract summary
        summary = ""
        parent = a_tag.find_parent(["div", "article", "li", "section"])
        if parent:
            for sel in summary_selector.split(","):
                el = parent.select_one(sel.strip())
                if el and el != a_tag:
                    s = _clean_text(el.get_text())
                    if len(s) > 10 and s != title:
                        summary = s
                        break

        # Try to extract image
        image = ""
        if parent:
            img = parent.find("img")
            if img:
                image = urljoin(url, img.get("src", "") or img.get("data-src", ""))

        # Try to extract date
        date_str = ""
        if parent:
            date_el = parent.select_one("time, .date, .time, .pub-date")
            if date_el:
                date_str = _parse_date(
                    date_el.get("datetime") or _clean_text(date_el.get_text())
                )

        articles.append({
            "id": _make_id(full_url, title),
            "title": title,
            "summary": summary[:150] + "..." if len(summary) > 150 else summary,
            "url": full_url,
            "source": source["name"],
            "base_url": source["base_url"],
            "date": date_str or datetime.now(timezone.utc).isoformat(),
            "image": image,
        })

    logger.info("HTML %s: found %d articles", source["name"], len(articles))
    return articles


# ── Main scraping orchestrator ──────────────────────────

def scrape_source(source):
    """Scrape a single source. Tries RSS first, falls back to HTML."""
    try:
        if source["type"] == "rss":
            articles = _scrape_rss(source)
            if not articles:
                logger.info("RSS failed for %s, trying HTML fallback", source["name"])
                # Try HTML fallback if scrape_url is available
                if "scrape_url" in source:
                    source_copy = dict(source)
                    source_copy["type"] = "html"
                    articles = _scrape_html(source_copy)
        else:
            articles = _scrape_html(source)

        return articles

    except Exception as e:
        logger.error("Error scraping %s: %s", source["name"], e, exc_info=True)
        return []


def scrape_all():
    """Scrape all configured sources and return combined articles."""
    all_articles = []
    for i, source in enumerate(config.SOURCES):
        logger.info("[%d/%d] Scraping: %s", i + 1, len(config.SOURCES), source["name"])
        articles = scrape_source(source)
        all_articles.extend(articles)
        if i < len(config.SOURCES) - 1:
            time.sleep(config.REQUEST_DELAY)

    # Deduplicate by URL
    seen = set()
    unique = []
    for art in all_articles:
        if art["url"] not in seen:
            seen.add(art["url"])
            unique.append(art)

    # Sort by date (newest first)
    unique.sort(key=lambda a: a.get("date", ""), reverse=True)

    logger.info("Total unique articles: %d", len(unique))
    return unique


def save_articles(articles):
    """Save articles to JSON file."""
    os.makedirs(os.path.dirname(config.DATA_FILE), exist_ok=True)
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(articles),
        "articles": articles,
    }
    with open(config.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d articles to %s", len(articles), config.DATA_FILE)
    return data


def load_articles():
    """Load articles from JSON file."""
    if not os.path.exists(config.DATA_FILE):
        return {"updated_at": None, "count": 0, "articles": []}
    with open(config.DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
