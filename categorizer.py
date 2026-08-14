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
    "车企", "车企", "厂商", "品牌",
    "buick", "chevrolet", "cadillac", "gm", "通用",
    "toyota", "honda", "nissan", "vw", "大众",
    "byd", "tesla", "nio", "理想", "小鹏", "蔚来",
    "model", "ev", "hev", "phev",
    "车", "轮", "胎", "刹",
]


def _has_auto_keyword(text):
    """Check if text contains at least one automotive keyword."""
    text_lower = text.lower()
    for kw in AUTO_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def classify_article(article):
    """
    Classify a single article into a category.
    Returns the category key (e.g. 'gm', 'competitor', 'policy') or None.
    Policy articles must also contain automotive-related keywords.
    """
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    scores = {}

    for cat_key, cat_def in CATEGORIES.items():
        score = 0
        for kw in cat_def["keywords"]:
            kw_lower = kw.lower()
            if kw_lower in text:
                # Longer keywords get higher weight
                score += len(kw_lower)
        scores[cat_key] = score

    # Pick the category with the highest score
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        # Policy articles must also be automotive-related
        if best_cat == "policy" and not _has_auto_keyword(text):
            return None
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
