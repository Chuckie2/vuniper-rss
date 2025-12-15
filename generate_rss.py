from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = "https://vuniper.com/"

fg = FeedGenerator()
fg.title("Vuniper – New Releases")
fg.link(href=URL)
fg.description("Unofficial RSS feed for new content on Vuniper")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle")
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")

# Grab all <a> tags as potential content links
links = soup.find_all("a", href=True)

seen = set()
for link in links:
    title = link.get_text(strip=True)
    href = link["href"]

    # Skip empty or trivial titles
    if not title or len(title) < 3:
        continue

    # Normalize relative URLs
    if href.startswith("/"):
        href = URL.rstrip("/") + href

    # Deduplicate links
    if href in seen:
        continue
    seen.add(href)

    # Add entry with timezone-aware datetime
    entry = fg.add_entry()
    entry.title(title)
    entry.link(href=href)
    entry.published(datetime.now(timezone.utc))  # timezone-aware
    entry.updated(datetime.now(timezone.utc))    # optional but avoids warnings

# Write RSS to file
fg.rss_file("rss.xml")
