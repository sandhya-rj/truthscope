import os
import re
import requests
import feedparser
from datetime import datetime
from rapidfuzz import fuzz

# Load environment variables early so other modules can read them
from dotenv import load_dotenv
load_dotenv()

# Try to import modern OpenAI client, fall back to legacy openai if necessary
client = None
OPENAI_MODE = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    # modern client (preferred)
    from openai import OpenAI
    if OPENAI_API_KEY:
        client = OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_MODE = "client"
    else:
        client = None
        OPENAI_MODE = None
except Exception:
    # fallback to legacy openai package
    try:
        import openai as legacy_openai
        legacy_openai.api_key = OPENAI_API_KEY
        client = legacy_openai
        OPENAI_MODE = "legacy"
    except Exception:
        client = None
        OPENAI_MODE = None

# ============================
# Trusted RSS feeds
# ============================
TRUSTED_RSS_URLS = [
    # Reuters
    "http://feeds.reuters.com/reuters/worldNews",
    "http://feeds.reuters.com/reuters/businessNews",
    # BBC
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/uk/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "https://feeds.bbci.co.uk/news/us_and_canada/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    # Al Jazeera
    "https://www.aljazeera.com/xml/rss/all.xml",
    # WHO (health-related)
    "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml",
]

trusted_items = []  # cache

# ============================
# API keys
# ============================
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

# ============================
# Helpers
# ============================
def normalize(text: str):
    """Lowercase and strip punctuation/numbers for better matching"""
    return re.sub(r"[^a-z0-9 ]+", "", (text or "").lower())

def fetch_rss_once():
    """Fetch and update trusted RSS cache"""
    new = []
    for url in TRUSTED_RSS_URLS:
        d = feedparser.parse(url)
        if not hasattr(d, "entries") or not d.entries:
            continue
        for entry in d.entries:
            item = {
                "source": url,
                "headline": entry.title,
                "link": entry.link,  # ✅ actual article link
                "timestamp": entry.get("published", str(datetime.utcnow())),
            }
            if not any(i["headline"] == item["headline"] for i in trusted_items):
                trusted_items.append(item)
                new.append(item)
    return new

def stream_trusted_news():
    """Return the latest trusted headlines"""
    fetch_rss_once()
    return trusted_items[-15:]

# ============================
# Fake news / headline check
# ============================
def check_news(headline: str):
    fetch_rss_once()
    norm_headline = normalize(headline)

    # Step 1: Collect evidence
    evidence = []

    # RSS fuzzy match
    rss_matches = [
        item for item in trusted_items
        if fuzz.token_set_ratio(norm_headline, normalize(item["headline"])) > 60
    ]
    for m in rss_matches:
        evidence.append(f"{m['headline']} ({m['link']})")

    # NewsAPI search
    if NEWS_API_KEY:
        try:
            res = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": headline,
                    "language": "en",
                    "pageSize": 5,
                    "apiKey": NEWS_API_KEY,
                },
                timeout=8,
            )
            data = res.json()
            for a in data.get("articles", []):
                evidence.append(f"{a.get('title')} ({a.get('url')})")
        except Exception as e:
            evidence.append(f"⚠ NewsAPI error: {e}")

    # GNews search
    if GNEWS_API_KEY:
        try:
            res = requests.get(
                "https://gnews.io/api/v4/search",
                params={
                    "q": headline,
                    "lang": "en",
                    "max": 5,
                    "token": GNEWS_API_KEY,
                },
                timeout=8,
            )
            data = res.json()
            for a in data.get("articles", []):
                evidence.append(f"{a.get('title')} ({a.get('url')})")
        except Exception as e:
            evidence.append(f"⚠ GNews API error: {e}")

    # Step 2: Use OpenAI to fact-check (if available)
    context = "\n".join(evidence) if evidence else "No evidence found in trusted sources."
    verdict_text = "⚠ OpenAI client not configured; skipped fact-check."  # default if client missing

    if client is None:
        # No OpenAI client available or key missing
        verdict_text = "⚠ OpenAI client not available or OPENAI_API_KEY not set."
    else:
        # Build messages for the model
        system_msg = (
            "You are a careful fact-checker. Given a short statement and a list of evidence links/headlines,"
            " decide whether the statement is true, false, misleading, or unverified. "
            "Provide a short verdict label (one line) and then a brief, human-friendly explanation "
            "that cites the evidence when possible. Keep it concise and clear."
        )
        user_msg = (
            f"Statement to fact-check:\n{headline}\n\n"
            f"Evidence collected:\n{context}\n\n"
            "Please respond with a short verdict label (like 'Verified Real' or 'Likely Fake') followed by "
            "a 2-5 sentence explanation in plain human language that cites any of the listed evidence links/headlines."
        )
        messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]

        # Try to call the modern client first; if that fails, try legacy ChatCompletion approach
        try:
            if OPENAI_MODE == "client":
                # modern OpenAI client
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=512,
                )
                # modern client returns choices[].message.content
                verdict_text = resp.choices[0].message.content.strip()
            else:
                # legacy openai package (openai.ChatCompletion.create)
                try:
                    resp = client.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=512,
                    )
                    verdict_text = resp["choices"][0]["message"]["content"].strip()
                except Exception:
                    # fallback to a widely available model name if gpt-4o-mini isn't supported
                    resp = client.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=512,
                    )
                    verdict_text = resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            # try a fallback model for the modern client if initial model fails
            try:
                if OPENAI_MODE == "client" and client is not None:
                    resp = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=512,
                    )
                    verdict_text = resp.choices[0].message.content.strip()
                else:
                    verdict_text = f"⚠ OpenAI error: {e}"
            except Exception as e2:
                verdict_text = f"⚠ OpenAI error: {e2}"

    # Simple heuristic to decide a short verdict label for UI (keeps compatibility with your frontend)
    vt = (verdict_text or "").lower()
    fake_tokens = ["fake", "false", "not true", "misleading", "fabricated", "no evidence", "unverified", "incorrect"]
    real_tokens = ["real", "true", "verified", "confirmed", "accurate", "substantiated", "supported", "yes"]

    verdict_label = "Unverified ❓"
    if any(tok in vt for tok in fake_tokens):
        verdict_label = "Potential Fake ❌"
    elif any(tok in vt for tok in real_tokens):
        verdict_label = "Verified Real ✅"

    return {
        "verdict": verdict_label,
        "evidence": evidence or ["No direct evidence found."],
        "explanation": verdict_text
    }
