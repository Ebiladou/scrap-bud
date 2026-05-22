import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils import save_to_excel
from .config import LIST_URL, SCHOOL_NAME, DELAY, HEADERS, OUTPUT_FILE

def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None

def get_all_society_stubs():
    soup = get_soup(LIST_URL)
    if not soup:
        return []

    stubs = []
    card = soup.find("ul", class_="mt-3")
    if not card:
        print("Could not find society list.")
        return []

    for li in card.find_all("li"):
        try:
            society = li.find("h3", class_="imperialH5")
            name = society.get_text(strip=True)
            a_tag = li.find("a")
            href  = a_tag["href"]
            stubs.append({"name": name, "href": href})
        except Exception as e:
            print(f"Skipped item: {e}")

    return stubs

def scrape_society_detail(stub):
    society_url = urljoin(LIST_URL, stub["href"])
    time.sleep(DELAY)

    soup = get_soup(society_url)
    president = "Not found"
    email = "Not found"

    if soup:
        president_tag = soup.find("h3", class_="imperialH1 mb-2")
        if president_tag:
            president = president_tag.get_text(strip=True)

        email_list = soup.find("ul", class_="isolate inline-flex w-full")
        if email_list:
            email_tag = email_list.find("a", href=lambda h: h and h.startswith("mailto:"))
            if email_tag:
                email = email_tag["href"].replace("mailto:", "")

    return {
        "school": SCHOOL_NAME,
        "name": stub["name"],
        "president": president,
        "email": email,
        "url": society_url,
    }

def main():
    stubs = get_all_society_stubs()

    print(f"Scraping detail pages for {len(stubs)} societies.\n")
    results = []

    for i, stub in enumerate(stubs, start=1):
        print(f"[{i}/{len(stubs)}] {stub['name']}")
        results.append(scrape_society_detail(stub))

        if i % 50 == 0:
            save_to_excel(results, OUTPUT_FILE)
            print(f"File saved at {i} rows.")

    save_to_excel(results, OUTPUT_FILE)

if __name__ == "__main__":
    main()