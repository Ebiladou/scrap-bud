from .config import OUTPUT_FILE
from .scrapy import get_all_society_stubs, scrape_society_detail
from ..utils import save_to_excel

def main():
    stubs = get_all_society_stubs()

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