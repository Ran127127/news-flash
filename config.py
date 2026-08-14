"""
Auto-News-Hub Configuration
============================
Sources, categories, and keyword definitions.
"""

# ============================================================
# Category definitions with keywords for auto-classification
# ============================================================
CATEGORIES = {
    "gm": {
        "name": "GM",
        "color": "#0052a2",
        "keywords": [
            # GM brands
            "\u901a\u7528\u6c7d\u8f66", "\u4e0a\u6c7d\u901a\u7528",
            "\u522b\u514b", "Buick", "GL8", "Encore", "Envision", "Enclave",
            "\u5a01\u9a81", "\u6602\u79d1\u5a01", "\u541b\u5a01", "\u5fae\u84dd", "E5", "E4",
            "\u96ea\u5f17\u5170", "Chevrolet", "Camaro", "Corvette", "Equinox",
            "\u8fc8\u9510\u5b9d", "\u63a2\u754c\u8005", "\u521c\u7eaa\u5143",
            "\u51ef\u8fea\u62c9\u514b", "Cadillac", "CT4", "CT5", "CT6",
            "XT4", "XT5", "XT6", "LYRIQ", "\u9510\u6b4c", "\u51ef\u96c5\u5fb7",
            "GMC", "\u8096\u79d1\u8fbe\u514b",
        ],
    },
    "competitor": {
        "name": "Competitor",
        "color": "#e63946",
        "keywords": [
            # Joint venture brands
            "\u4e30\u7530", "Toyota", "\u51ef\u7f8e\u745e", "\u96c5\u9601",
            "\u5927\u4f17", "Volkswagen", "\u5e15\u8428\u7279", "\u8fc8\u817e",
            "\u672c\u7530", "Honda", "\u5947\u745e", "\u96c5\u7ff0",
            "\u65e5\u4ea7", "Nissan", "\u5929\u7c41",
            "\u73b0\u4ee3", "Hyundai", "\u8d77\u4e9a",
            "\u5a01\u9f99", "Volvo", "\u5b9d\u9a6c", "BMW", "\u5954\u9a70",
            "Mercedes", "\u5965\u8fea", "Audi",
            # New energy brands
            "\u6bd4\u4e9a\u8fea", "BYD", "\u6c49\u817e", "\u6d77\u8c79", "\u5b8bPlus", "\u79e6Plus",
            "\u851a\u6765", "NIO", "ET5", "ET7", "ES6", "ES8",
            "\u5c0f\u9e4f", "XPeng", "P7", "G6", "G9",
            "\u7406\u60f3", "Li Auto", "L7", "L8", "L9",
            "\u54c1\u724c", "\u6781\u6c2a", "\u96f6\u8dd1", "\u54ea\u5412",
            "\u7279\u65af\u62c9", "Tesla", "Model 3", "Model Y",
            "\u5e7f\u6c7d\u57c3\u5b89", "\u957f\u57ce\u6c7d\u8f66", "\u5409\u5229", "\u5947\u745e",
            "\u65b0\u80fd\u6e90", "\u7eaf\u7535", "\u63d2\u6df7", "\u589e\u7a0b",
            "\u84dd\u56fe", "\u6df1\u84dd", "\u6d77\u72ee", "\u8c47\u5854",
        ],
    },
    "policy": {
        "name": "Policy",
        "color": "#2d6a4f",
        "keywords": [
            "\u653f\u7b56", "\u6cd5\u89c4", "\u6807\u51c6", "\u8865\u8d34",
            "\u65b0\u80fd\u6e90\u8865\u8d34", "\u8d2d\u7f6e\u7a0e", "\u8f66\u8231\u7a0e",
            "\u53cc\u79ef\u5206", "\u78b3\u4e2d\u548c", "\u78b3\u8fbe\u5cf0",
            "\u6392\u653e\u6807\u51c6", "\u56fd\u516d", "\u56fd\u4e03",
            "\u514d\u9650\u884c", "\u9650\u884c", "\u724c\u7167",
            "\u5145\u7535\u6869", "\u52a0\u6c22\u7ad9", "\u57fa\u7840\u8bbe\u65bd",
            "\u6c7d\u8f66\u4e0b\u4e61", "\u4ee5\u65e7\u6362\u65b0", "\u62a5\u5e9f",
            "\u4ea7\u4e1a\u653f\u7b56", "\u51c6\u5165", "\u76d1\u7ba1",
            "\u4ea4\u901a\u90e8", "\u5de5\u4fe1\u90e8", "\u53d1\u6539\u59d4",
            "\u5b89\u5168\u6cd5\u89c4", "\u53ec\u56de", "\u7f3a\u9677",
            "\u667a\u80fd\u9a7e\u9a76", "\u81ea\u52a8\u9a7e\u9a76", "\u6cd5\u89c4",
            "L3", "L4", "\u8def\u6d4b", "\u7248\u53d1",
        ],
    },
}

# ============================================================
# Source definitions
# ============================================================
# Each source has:
#   name:        Display name
#   base_url:    Homepage URL (for linking)
#   type:        "rss" or "html"
#   feed_url:    (rss) RSS feed URL
#   scrape_url:  (html) Page URL to scrape
#   selectors:   (html) dict with article_link, title, summary, date CSS selectors
#   max_items:   Max articles to fetch per scrape (default 15)

SOURCES = [
    # ── GM Dedicated ────────────────────────────────────
    {
        "name": "GM Authority",
        "base_url": "https://gmauthority.com",
        "type": "rss",
        "feed_url": "https://gmauthority.com/feed/",
        "max_items": 20,
    },
    # ── Chinese Auto Media ──────────────────────────────
    {
        "name": "\u6c7d\u8f66\u4e4b\u5bb6",
        "base_url": "https://www.autohome.com.cn",
        "type": "html",
        "scrape_url": "https://www.autohome.com.cn/news/",
        "selectors": {
            "article_link": "a[href*='/news/']",
            "title": "h3, h4, .title",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u592a\u5e73\u6d0b\u6c7d\u8f66",
        "base_url": "https://www.pcauto.com.cn",
        "type": "html",
        "scrape_url": "https://www.pcauto.com.cn/nation/",
        "selectors": {
            "article_link": "a[href*='/nation/']",
            "title": "h3, .title",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u6613\u8f66\u7f51",
        "base_url": "https://www.yiche.com",
        "type": "html",
        "scrape_url": "https://news.yiche.com/hao/wenzhang/",
        "selectors": {
            "article_link": "a[href*='/hao/']",
            "title": "h3, h4, .title",
            "summary": ".summary, .desc, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u61c2\u8f66\u5e1d",
        "base_url": "https://www.dongchedi.com",
        "type": "html",
        "scrape_url": "https://www.dongchedi.com/auto/library/x-x-x-x-x-x-x-x-x-x-x-x-x-x-x",
        "selectors": {
            "article_link": "a[href*='/article/']",
            "title": ".title, h3",
            "summary": ".desc, .summary",
        },
        "max_items": 15,
    },
    {
        "name": "\u65b0\u8f66\u8bc4",
        "base_url": "https://www.xincheping.com",
        "type": "html",
        "scrape_url": "https://www.xincheping.com/",
        "selectors": {
            "article_link": "a[href*='/article/'], a[href*='/']",
            "title": "h3, h2, .title",
            "summary": ".desc, .summary, p",
        },
        "max_items": 10,
    },
    {
        "name": "\u6c7d\u8f66\u516c\u793e",
        "base_url": "https://www.ichongyi.info",
        "type": "html",
        "scrape_url": "https://www.ichongyi.info/",
        "selectors": {
            "article_link": "a[href*='/archives/'], a[href*='/post/']",
            "title": "h2, h3, .entry-title",
            "summary": ".excerpt, .entry-summary, p",
        },
        "max_items": 10,
    },
    {
        "name": "36\u6c2a\u6c7d\u8f66",
        "base_url": "https://www.36kr.com",
        "type": "html",
        "scrape_url": "https://www.36kr.com/information/auto/",
        "selectors": {
            "article_link": "a[href*='/p/']",
            "title": ".article-item-title, h3, .title",
            "summary": ".article-item-description, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u7b2c\u4e00\u7535\u52a8",
        "base_url": "https://www.d1ev.com",
        "type": "html",
        "scrape_url": "https://www.d1ev.com/news",
        "selectors": {
            "article_link": "a[href*='/news/']",
            "title": "h3, h4, .title",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
    # ── International Auto Media ────────────────────────
    {
        "name": "Motor1",
        "base_url": "https://www.motor1.com",
        "type": "html",
        "scrape_url": "https://www.motor1.com/news/",
        "selectors": {
            "article_link": "a[href*='/news/']",
            "title": "h2, h3, .title",
            "summary": ".summary, .excerpt, p",
        },
        "max_items": 15,
    },
    {
        "name": "Autocar UK",
        "base_url": "https://www.autocar.co.uk",
        "type": "html",
        "scrape_url": "https://www.autocar.co.uk/car-news",
        "selectors": {
            "article_link": "a[href*='/car-news/']",
            "title": "h3, .title, .field-name-title",
            "summary": ".intro, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "CarNewsChina",
        "base_url": "https://carnewschina.com",
        "type": "rss",
        "feed_url": "https://carnewschina.com/feed/",
        "max_items": 15,
    },
    {
        "name": "InsideEVs",
        "base_url": "https://insideevs.com",
        "type": "html",
        "scrape_url": "https://insideevs.com/news/",
        "selectors": {
            "article_link": "a[href*='/news/']",
            "title": "h2, h3, .title",
            "summary": ".subtitle, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "Electrek",
        "base_url": "https://electrek.co",
        "type": "rss",
        "feed_url": "https://electrek.co/feed/",
        "max_items": 15,
    },
    # ── Government Policy Sources ───────────────────────
    {
        "name": "\u5de5\u4e1a\u548c\u4fe1\u606f\u5316\u90e8",
        "base_url": "https://www.miit.gov.cn",
        "type": "html",
        "scrape_url": "https://www.miit.gov.cn/xwdt/index.html",
        "selectors": {
            "article_link": "a[href*='art/']",
            "title": "h3, h4, .title",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u56fd\u5bb6\u53d1\u5c55\u548c\u6539\u9769\u59d4\u5458\u4f1a",
        "base_url": "https://www.ndrc.gov.cn",
        "type": "html",
        "scrape_url": "https://www.ndrc.gov.cn/xwdt/xwfb/index.html",
        "selectors": {
            "article_link": "a[href*='t202']",
            "title": "h3, h4, .title",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u4ea4\u901a\u8fd0\u8f93\u90e8",
        "base_url": "https://www.mot.gov.cn",
        "type": "html",
        "scrape_url": "https://www.mot.gov.cn/xinwen/jiaotongyaowen/index.html",
        "selectors": {
            "article_link": "a[href*='t202']",
            "title": "h3, h4, .title",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u5546\u52a1\u90e8",
        "base_url": "https://www.mofcom.gov.cn",
        "type": "html",
        "scrape_url": "https://www.mofcom.gov.cn/",
        "selectors": {
            "article_link": "a[href*='art/202']",
            "title": "h3, h4, li",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
    {
        "name": "\u4e2d\u56fd\u653f\u5e9c\u7f51",
        "base_url": "https://www.gov.cn",
        "type": "html",
        "scrape_url": "https://www.gov.cn/",
        "selectors": {
            "article_link": "a[href*='content_']",
            "title": "h4, h3, li",
            "summary": ".desc, .summary, p",
        },
        "max_items": 15,
    },
]

# ============================================================
# Scraping settings
# ============================================================
REQUEST_TIMEOUT = 15          # seconds
REQUEST_DELAY = 1.5           # seconds between requests (be polite)
MAX_RETRIES = 2
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
DATA_FILE = "data/articles.json"
MAX_ARTICLES_PER_CATEGORY = 50  # max articles to display per category

# ============================================================
# Server settings
# ============================================================
import os

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
