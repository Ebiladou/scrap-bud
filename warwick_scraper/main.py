import re
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from utils import save_to_excel
from .config import DELAY, HEADERS, LIST_URL, OUTPUT_FILE, SCHOOL_NAME


PRESIDENT_PATTERNS = [
    r"co[- ]?presidents?\s*[:-]\s*(.*?)(?=\b(?:vice|treasurer|secretary|social|welfare|outreach|publicity)\b|$)",
    r"presidents?\s*[:-]\s*(.*?)(?=\b(?:vice|treasurer|secretary|social|welfare|outreach|publicity)\b|$)",
]


def extract_president(soup):
    for elem in soup.find_all(["p", "li", "dt", "dd"]):
        text = elem.get_text(" ", strip=True)
        for pattern in PRESIDENT_PATTERNS:
            match = re.search(pattern, text, re.I)
            if match:
                name = match.group(1)
                name = re.sub(r"\S+@\S+", "", name)
                name = re.sub(r"\(.*?\)", "", name)
                name = name.strip(" -|:;,. ")
                name = " ".join(name.split())
                if name:
                    return name
    return "Not found"

def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def get_all_society_stubs():
    print(f"Loading {LIST_URL} ...")
    soup = get_soup(LIST_URL)
    if not soup:
        return []

    card = soup.find("ul", class_="msl_organisation_list")
    if not card:
        print("Society list not found.")
        return []

    stubs = []
    for li in card.find_all("li", attrs={"data-msl-grouping-id": True}):
        link = li.find("a", class_="msl-gl-link")
        if not link:
            continue
        stubs.append({
            "name": link.get_text(strip=True),
            "href": link["href"],
        })

    print(f"Found {len(stubs)} societies.\n")
    return stubs


def scrape_society_detail(stub):
    society_url = urljoin(LIST_URL, stub["href"])
    time.sleep(DELAY)

    president = "Not found"
    email = "Not found"

    soup = get_soup(society_url)
    if soup:
        mail_div = soup.find("div", class_="mailLink")
        if mail_div:
            email_link = mail_div.find("a", class_="msl_email")
            if email_link:
                email = email_link["href"].replace("mailto:", "").strip()

        president = extract_president(soup)

    return {
        "school": SCHOOL_NAME,
        "name": stub["name"],
        "president": president,
        "email": email,
        "url": society_url,
    }

def main():
    stubs = get_all_society_stubs()

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