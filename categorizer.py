"""
News Flash Categorizer
======================
Classify articles into categories based on keyword matching.
"""

import logging
from config import CATEGORIES

logger = logging.getLogger(__name__)


def classify_article(article):
    """
    Classify a single article into a category.
    Returns the category key (e.g. 'gm', 'competitor', 'policy') or None.
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
