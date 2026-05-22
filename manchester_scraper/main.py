import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from utils import save_to_excel
from .config import LIST_URL, SCHOOL_NAME, OUTPUT_FILE, DELAY, HEADERS

def safe_goto(page, url, timeout=60000):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout)
    except PlaywrightTimeoutError:
        page.goto(url, wait_until="commit", timeout=timeout)


def get_all_society_stubs(page):
    stubs = []

    print(f"Loading {LIST_URL}")
    safe_goto(page, LIST_URL)

    try:
        page.wait_for_selector("div.list", timeout=15000)
    except PlaywrightTimeoutError:
        print("Activity list selector never appeared.")
        return stubs

    clicks = 0
    while True:
        try:
            show_more = page.locator("button#see-more").first
            if not show_more.is_visible(timeout=3000):
                break
            show_more.click()
            clicks += 1
            page.wait_for_timeout(1500)
        except Exception:
            break

    soup = BeautifulSoup(page.content(), "html.parser")
    card = soup.find("div", class_="list")
    if not card:
        print("Activity list not found.")
        return stubs

    for div in card.find_all("div", class_="activity"):
        society_tag = div.find("span", class_="title")
        anchor = div.find("a")
        if not society_tag or not anchor:
            continue
        stubs.append({
            "name": society_tag.get_text(strip=True),
            "href": anchor["href"],
        })

    print(f"Found {len(stubs)} societies.\n")
    return stubs


def scrape_society_detail(browser, stub):
    society_url = urljoin(LIST_URL, stub["href"])

    society_page = browser.new_page()
    society_page.set_extra_http_headers(HEADERS)

    try:
        safe_goto(society_page, society_url)
        soup = BeautifulSoup(society_page.content(), "html.parser")

        email = "Not found"
        contact_div = soup.find("div", class_="contactinfo")
        if contact_div:
            email_tag = contact_div.find("a", href=lambda h: h and h.startswith("mailto:"))
            if email_tag:
                email = email_tag["href"].replace("mailto:", "")

    except Exception as e:
        print(f"[ERROR] {society_url}: {e}")
        email = "Not found"
    finally:
        society_page.close()

    time.sleep(DELAY)

    return {
        "school": SCHOOL_NAME,
        "name": stub["name"],
        "president": "Not found",
        "email": email,
        "url": society_url,
    }


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        list_page = browser.new_page()
        list_page.set_extra_http_headers(HEADERS)

        stubs = get_all_society_stubs(list_page)
        list_page.close()

        print(f"Scraping detail pages for {len(stubs)} societies...\n")
        results = []

        for i, stub in enumerate(stubs, start=1):
            print(f"[{i}/{len(stubs)}] {stub['name']}")
            results.append(scrape_society_detail(browser, stub))

            if i % 50 == 0:
                save_to_excel(results, OUTPUT_FILE)
                print(f"Checkpoint saved at {i} rows.")

        browser.close()

    save_to_excel(results, OUTPUT_FILE)

if __name__ == "__main__":
    main()