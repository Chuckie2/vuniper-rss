from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

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

# This selector is intentionally broad to survive layout changes
links = soup.select("a[href]")

seen = set()
for link in links:
    title = link.get_text(strip=True)
    href = link.get("href")

    if not title or len(title) < 3:
        continue

    if href.startswith("/"):
        href = URL.rstrip("/") + href

    if href in seen:
        continue
    seen.add(href)

    entry = fg.add_entry()
    entry.title(title)
    entry.link(href=href)
    entry.published(datetime.now(timezone.utc))

fg.rss_file("rss.xml")
