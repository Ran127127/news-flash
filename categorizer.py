"""
News Flash Categorizer
======================
Classify articles into categories based on keyword matching.
"""

import logging
from config import CATEGORIES

logger = logging.getLogger(__name__)

# Automotive-related keywords for Policy validation
# Policy articles must also contain at least one of these to be classified as Policy
AUTO_KEYWORDS = [
    "汽车", "车辆", "轿车", "客车", "货车", "卡车",
    "新能源", "电动车", "燃油车", "混动", "插电",
    "驾驶", "行驶", "车道", "公路", "高速", "道路",
    "交通", "运输", "出行", "乘车",
    "车牌", "驾照", "违章", "事故",
    "发动机", "电池", "充电", "续航",
    "车企", "厂商", "品牌",
    "buick", "chevrolet", "cadillac", "gm", "通用",
    "toyota", "honda", "nissan", "vw", "大众",
    "byd", "tesla", "nio", "理想", "小鹏", "蔚来",
    "model", "ev", "hev", "phev",
    "车", "轮", "胎", "刹",
]

# Government sources — articles from these are forced into Policy only.
# They must NOT leak into GM / Competitor even if they mention brand names.
GOV_SOURCES = {
    "工业和信息化部",
    "国家发展和改革委员会",
    "交通运输部",
    "商务部",
    "中国政府网",
}

# Source-name hints: government sources whose mandate inherently covers
# automotive / transport policy.  When an article comes from one of these
# sources we inject extra context so the auto-keyword gate is not too strict.
SOURCE_AUTO_HINT = {
    "工业和信息化部": ["工业", "制造", "产业", "汽车", "新能源", "充电", "车企"],
    "交通运输部":     ["交通", "运输", "公路", "高速", "出行", "道路"],
    "国家发展和改革委员会": ["发改", "经济", "价格", "产业"],
    "商务部":         ["商务", "贸易", "消费", "汽车", "出口"],
    "中国政府网":     ["交通", "运输", "汽车"],
}


def _has_auto_keyword(article):
    """
    Check if an article is automotive-related.
    Combines the article's title+summary with source-name hints.
    """
    text = (
        article.get("title", "")
        + " " + article.get("summary", "")
        + " " + article.get("source", "")
    ).lower()

    # Add source-specific hints
    source = article.get("source", "")
    for src_name, hints in SOURCE_AUTO_HINT.items():
        if src_name in source:
            text += " " + " ".join(hints)

    text_lower = text.lower()
    for kw in AUTO_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def classify_article(article):
    """
    Classify a single article into a category.
    Returns the category key (e.g. 'gm', 'competitor', 'policy') or None.

    Government-source articles are forced into Policy only (if they pass
    the automotive relevance check).  All other sources use normal scoring.
    """
    source = article.get("source", "")
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()

    # ── Government sources → Policy only ──────────────────
    if source in GOV_SOURCES:
        policy_score = 0
        for kw in CATEGORIES["policy"]["keywords"]:
            if kw.lower() in text:
                policy_score += len(kw.lower())
        if policy_score > 0 and _has_auto_keyword(article):
            return "policy"
        return None

    # ── Normal scoring for all other sources ──────────────
    scores = {}
    for cat_key, cat_def in CATEGORIES.items():
        score = 0
        for kw in cat_def["keywords"]:
            kw_lower = kw.lower()
            if kw_lower in text:
                score += len(kw_lower)
        scores[cat_key] = score

    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        return best_cat
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
