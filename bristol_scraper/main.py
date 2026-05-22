import re
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from utils import save_to_excel
from .config import DELAY, EMAIL_REGEX, HEADERS, LIST_URL, OUTPUT_FILE, SCHOOL_NAME


def safe_goto(page, url, timeout=60000):
    try:
        return page.goto(url, wait_until="domcontentloaded", timeout=timeout)
    except PlaywrightTimeoutError:
        return page.goto(url, wait_until="commit", timeout=timeout)


def clean_email(email):
    if not email:
        return None
    email = email.strip().replace("mailto:", "").split("?")[0]
    return email if re.match(EMAIL_REGEX, email) else None


def extract_email(soup):
    sections = []
    for selector in ["section#contact-us", "section.socials", ".contact-us", ".contentBoxes"]:
        sections += soup.select(selector)

    emails = []
    for section in sections:
        for anchor in section.select('a[href^="mailto:"]'):
            email = clean_email(anchor.get("href"))
            if email:
                emails.append(email)
        emails += re.findall(EMAIL_REGEX, section.get_text(" ", strip=True))

    filtered = []
    for email in emails:
        email = clean_email(email)
        if not email:
            continue
        if "bristolsu@" in email and len(emails) > 1:
            continue
        filtered.append(email)

    return filtered[0] if filtered else "Not found"


def extract_president(soup):
    container = soup.find("div", class_="contentBoxes") or soup
    for line in container.get_text("\n", strip=True).split("\n"):
        line = line.strip()
        if "vice" in line.lower():
            continue
        match = re.search(r"President\s*:\s*(.+)", line, re.I)
        if match:
            name = match.group(1).strip()
            if len(name) > 2 and "email" not in name.lower() and "vice" not in name.lower():
                return name
    return "Not found"


def get_all_society_stubs(browser):
    page = browser.new_page()
    page.set_extra_http_headers(HEADERS)

    safe_goto(page, LIST_URL)
    page.wait_for_selector("a.group-box", timeout=30000)

    previous_count = 0
    clicks = 0

    while True:
        current_count = page.locator("a.group-box").count()
        if current_count == previous_count and clicks > 0:
            print("No new societies loaded.")
            break

        previous_count = current_count
        load_more = page.locator("a.uc-load-more-groups")

        try:
            if load_more.count() == 0:
                break

            if not load_more.first.is_visible():
                print("Load more button not visible.")
                break

            load_more.first.scroll_into_view_if_needed()
            load_more.first.click(force=True)

            clicks += 1

            page.wait_for_load_state("networkidle")
            time.sleep(2)

        except Exception as e:
            print("Error clicking load more:", repr(e))
            break

    soup = BeautifulSoup(page.content(), "html.parser")

    stubs = []
    for anchor in soup.select("a.group-box"):
        name_tag = anchor.select_one("div.group-name")
        href = anchor.get("href")

        if not name_tag or not href:
            continue

        stubs.append({
            "name": name_tag.get_text(strip=True),
            "href": href,
        })

    print(f"Found {len(stubs)} societies")

    page.close()
    return stubs


def scrape_society_detail(stub):
    society_url = urljoin(LIST_URL, stub["href"])
    time.sleep(DELAY)

    president = "Not found"
    email = "Not found"

    try:
        response = requests.get(society_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        president = extract_president(soup)
        email = extract_email(soup)
    except Exception as e:
        print(f"[ERROR] {society_url}: {e}")

    return {
        "school": SCHOOL_NAME,
        "name": stub["name"],
        "president": president,
        "email": email,
        "url": society_url,
    }


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        stubs = get_all_society_stubs(browser)
        browser.close()

    print(f"Scraping detail pages for {len(stubs)} societies...\n")
    results = []

    for i, stub in enumerate(stubs, start=1):
        print(f"[{i}/{len(stubs)}] {stub['name']}")
        results.append(scrape_society_detail(stub))

        if i % 50 == 0:
            save_to_excel(results, OUTPUT_FILE)
            print(f"Checkpoint saved at {i} rows.")

    save_to_excel(results, OUTPUT_FILE)


if __name__ == "__main__":
    main()
