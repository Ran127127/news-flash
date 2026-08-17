"""
News Flash Categorizer
======================
Strict source-aware classification:
  - Policy:     ONLY official government sources with automotive relevance
  - GM:         ONLY GM company & its brands (Cadillac, Buick, Chevrolet)
  - Competitor: ONLY competitor brand news
"""

import logging
from config import CATEGORIES

logger = logging.getLogger(__name__)

# ── Government sources → Policy only ──────────────────────────
# Articles from these sources can ONLY go to Policy.
# They must NOT leak into GM / Competitor even if they mention brand names.
GOV_SOURCES = {
    "工业和信息化部",
    "国家发展和改革委员会",
    "交通运输部",
    "商务部",
    "中国政府网",
}

# Source-name hints: inject implicit automotive context for government
# sources so the auto-keyword gate is not too strict on sparse summaries.
SOURCE_AUTO_HINT = {
    "工业和信息化部":       ["工业", "制造", "产业", "汽车", "新能源", "充电", "车企"],
    "交通运输部":           ["交通", "运输", "公路", "高速", "出行", "道路"],
    "国家发展和改革委员会": ["发改", "经济", "价格", "产业"],
    "商务部":               ["商务", "贸易", "消费", "汽车", "出口"],
    "中国政府网":           ["交通", "运输", "汽车"],
}

# Automotive keywords used to validate government-source articles
AUTO_KEYWORDS = [
    "汽车", "车辆", "轿车", "客车", "货车", "卡车",
    "新能源", "电动车", "燃油车", "混动", "插电",
    "驾驶", "行驶", "车道", "公路", "高速", "道路",
    "交通", "运输", "出行", "乘车",
    "车牌", "驾照", "违章", "事故",
    "发动机", "电池", "充电", "续航",
    "车企", "厂商",
    "buick", "chevrolet", "cadillac", "gm", "通用",
    "toyota", "honda", "nissan", "vw", "大众",
    "byd", "tesla", "nio", "理想", "小鹏", "蔚来",
    "model", "ev", "hev", "phev",
    "车", "轮", "胎", "刹",
]


def _has_auto_keyword(article):
    """
    Check if a government-source article is automotive-related.
    Combines title + summary + source name + source-specific hints.
    """
    text = (
        article.get("title", "")
        + " " + article.get("summary", "")
        + " " + article.get("source", "")
    )

    source = article.get("source", "")
    for src_name, hints in SOURCE_AUTO_HINT.items():
        if src_name in source:
            text += " " + " ".join(hints)

    text_lower = text.lower()
    for kw in AUTO_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def _score_text(text, keywords):
    """Sum of keyword lengths for all keywords found in text."""
    score = 0
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            score += len(kw.lower())
    return score


def classify_article(article):
    """
    Classify a single article into a category.

    Rules:
      1. Government sources → Policy ONLY (if automotive-related).
      2. Non-government sources → GM or Competitor by keyword scoring.
         Policy is NOT available to non-government sources (media reports
         about policy are not "official policy news").
    """
    source = article.get("source", "")
    text = article.get("title", "") + " " + article.get("summary", "")

    # ── Government sources → Policy only ──────────────────────
    if source in GOV_SOURCES:
        policy_score = _score_text(text, CATEGORIES["policy"]["keywords"])
        if policy_score > 0 and _has_auto_keyword(article):
            return "policy"
        return None

    # ── Non-government sources → GM or Competitor only ────────
    gm_score = _score_text(text, CATEGORIES["gm"]["keywords"])
    comp_score = _score_text(text, CATEGORIES["competitor"]["keywords"])

    # GM Authority source defaults to GM if no strong competitor signal
    if source == "GM Authority" and gm_score == 0:
        return "gm"

    if gm_score > 0 or comp_score > 0:
        if gm_score >= comp_score:
            return "gm"
        return "competitor"

    return None


def categorize_articles(articles):
    """
    Categorize a list of articles.
    Returns a dict: {category_key: [articles], ...}
    Each article gets an added 'category' field.
    Articles that don't match any category are silently dropped.
    """
    result = {key: [] for key in CATEGORIES}
    dropped = 0

    for article in articles:
        cat = classify_article(article)
        if cat is not None:
            article["category"] = cat
            result[cat].append(article)
        else:
            dropped += 1

    # Log summary
    for cat_key, arts in result.items():
        name = CATEGORIES.get(cat_key, {}).get("name", cat_key)
        logger.info("Category '%s' (%s): %d articles", cat_key, name, len(arts))
    if dropped:
        logger.info("Dropped %d uncategorized articles", dropped)

    return result
