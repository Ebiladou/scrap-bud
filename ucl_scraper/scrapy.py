import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .config import BASE_URL, LIST_URL, SCHOOL_NAME, DELAY, HEADERS

def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None

def get_all_society_stubs():
    stubs = []
    page_num = 0

    while True:
        url = LIST_URL if page_num == 0 else f"{LIST_URL}?page={page_num}"

        soup = get_soup(url)
        if not soup:
            break

        cards = soup.find_all("div", class_="col_auto")
        if not cards:
            print(f"No cards on page {page_num + 1} — stopping.")
            break

        for card in cards:
            try:
                name = card.find("div", class_="card_title_field").get_text(strip=True)
                link_tag = card.find("a", class_="card-link")
                href = link_tag["href"]
                stubs.append({"name": name, "href": href})
            except Exception as e:
                print(f"Skipped card: {e}")

        if len(cards) < 24:
            break

        page_num += 1
        time.sleep(DELAY)

    return stubs

def scrape_society_detail(stub):
    society_url = urljoin(BASE_URL, stub["href"])
    time.sleep(DELAY)

    soup = get_soup(society_url)
    president = "Not found"
    email = "Not found"

    if soup:
        president_div = soup.find("div", class_="field--name-field-current-president-computed")
        if president_div:
            li = president_div.find("li")
            if li:
                president = li.get_text(strip=True)

        email_div = soup.find("div", class_="field--name-field-email")
        if email_div:
            email_link = email_div.find("a", class_="email-button")
            if email_link:
                email = email_link.get("data-email", "Not found")

    return {
        "school": SCHOOL_NAME,
        "name": stub["name"],
        "president": president,
        "email": email,
        "url": society_url,
    }