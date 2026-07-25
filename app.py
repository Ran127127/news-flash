"""
News Flash - Flask Application
================================
Main web app with scheduled scraping.
"""

import logging
import sys
from datetime import datetime, timezone

from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

import config
from scraper import scrape_all, save_articles, load_articles
from categorizer import categorize_articles

# ── Logging ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("auto-news-hub.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ── Flask app ───────────────────────────────────────────
app = Flask(__name__)


def run_update():
    """Run a full scrape + categorize + save cycle."""
    logger.info("=" * 50)
    logger.info("Starting scheduled update...")
    try:
        articles = scrape_all()
        data = save_articles(articles)
        categorized = categorize_articles(articles)
        total = sum(len(v) for v in categorized.values())
        logger.info("Update complete: %d articles categorized", total)
        return data
    except Exception as e:
        logger.error("Update failed: %s", e, exc_info=True)
        return None


# ── Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    """Main dashboard page."""
    data = load_articles()
    articles = data.get("articles", [])
    categorized = categorize_articles(articles)

    # Prepare category info
    categories = []
    for key, cat_def in config.CATEGORIES.items():
        cat_articles = categorized.get(key, [])
        categories.append({
            "key": key,
            "name": cat_def["name"],
            "color": cat_def["color"],
            "count": len(cat_articles),
            "articles": cat_articles[:config.MAX_ARTICLES_PER_CATEGORY],
        })

    updated_at = data.get("updated_at")
    if updated_at:
        try:
            dt = datetime.fromisoformat(updated_at)
            updated_at = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    return render_template(
        "index.html",
        categories=categories,
        updated_at=updated_at or "\u4ece\u672a\u66f4\u65b0",
        total_count=data.get("count", 0),
    )


@app.route("/api/update", methods=["POST"])
def api_update():
    """Trigger a manual update."""
    logger.info("Manual update triggered")
    data = run_update()
    if data:
        return jsonify({"status": "ok", "count": data.get("count", 0)})
    return jsonify({"status": "error", "message": "Update failed"}), 500


@app.route("/api/articles")
def api_articles():
    """Return all articles as JSON."""
    data = load_articles()
    category = None
    from flask import request
    if request.args.get("category"):
        category = request.args.get("category")
        articles = [
            a for a in data.get("articles", [])
            if a.get("category") == category
        ]
        return jsonify({"articles": articles, "count": len(articles)})
    return jsonify(data)


@app.route("/health")
def health():
    """Health check endpoint for Render."""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/sources")
def api_sources():
    """Return configured sources."""
    sources = [
        {"name": s["name"], "base_url": s["base_url"], "type": s["type"]}
        for s in config.SOURCES
    ]
    return jsonify({"sources": sources, "count": len(sources)})


# ── Scheduler ───────────────────────────────────────────

def init_scheduler():
    """Set up the daily 8 AM scraping schedule."""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        run_update,
        "cron",
        hour=8,
        minute=0,
        id="daily_update",
        name="Daily content update",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started: daily update at 08:00")
    return scheduler


# ── Main ────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("News Flash starting...")
    logger.info("Dashboard: http://localhost:%d", config.PORT)

    # Run initial scrape if no data exists
    data = load_articles()
    if data.get("count", 0) == 0:
        logger.info("No existing data, running initial scrape...")
        run_update()

    # Start scheduler
    scheduler = init_scheduler()

    try:
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            use_reloader=False,  # Don't double-start scheduler
        )
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Shutting down...")
