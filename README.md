# University Society Scrapers

This project contains small educational web scrapers for collecting public society information from university student union websites. The scrapers use Python, Beautiful Soup, Requests, Playwright, and OpenPyXL to load society listing pages, inspect individual society pages, extract useful fields, and save the result to Excel.

The code is intended for learning and experimentation.

## Project Structure

```text
.
|-- bristol_scraper/
|   |-- config.py
|   `-- main.py
|-- imperial_scraper/
|   |-- config.py
|   `-- main.py
|-- manchester_scraper/
|   |-- config.py
|   `-- main.py
|-- ucl_scraper/
|-- warwick_scraper/
|   |-- config.py
|   `-- main.py
|-- bristol.py
|-- war.py
|-- test.py
|-- utils.py
|-- requirements.txt
`-- .env
```

Each scraper package follows the same basic design:

- `config.py` loads school-specific values from `.env`.
- `main.py` contains the scraping logic for that school.
- `utils.py` contains shared Excel export logic.

## Environment Variables

The project stores configurable values in `.env` so URLs, school names, and output file names are not hardcoded inside the scraping logic.

Current variables include:

```text
BASE_URL=
LIST_URL=
OUTPUT_FILE=
SCHOOL_NAME=

IMP_LIST_URL=
IMP_NAME=
IMP_OUTPUT_FILE=

MAN_LIST_URL=
MAN_NAME=
MAN_OUTPUT_FILE=

WAR_LIST_URL=
WAR_NAME=
WAR_OUTPUT_FILE=

BRI_LIST_URL=
BRI_NAME=
BRI_OUTPUT_FILE=

TEST_LIST_URL=
TEST_SCHOOL_NAME=
```

The exploratory `test.py` file stays at the project root, but it now reads `TEST_LIST_URL` and `TEST_SCHOOL_NAME` from `.env`.

## Installation

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

`playwright install` downloads the browser binaries that Playwright needs.

## Running The Scrapers

Run a scraper from the project root:

```bash
python -m imperial_scraper.main
python -m manchester_scraper.main
```

Each script prints progress in the terminal and writes an Excel file using the configured output path.

## What Beautiful Soup Does Here

Beautiful Soup is the HTML parsing library used throughout the project. It does not browse the web by itself. Instead, it receives HTML from either `requests` or Playwright and turns that HTML into a searchable Python object.

The scrapers use Beautiful Soup to:

- Find society listing containers.
- Select society cards or list items.
- Extract society names and links.
- Open each detail page and parse contact sections.
- Find email links with `mailto:` URLs.
- Search visible text for committee roles such as president.

For pages that are already present in the initial HTML response, Requests plus Beautiful Soup is enough. Warwick follows this pattern: the society list and detail information can be loaded with normal HTTP requests, then parsed with Beautiful Soup selectors.

## What Playwright Does Here

Playwright is a browser automation library. It opens a real browser engine, waits for the page to render, clicks buttons, and then exposes the final page HTML.

This matters because some student union websites do not send the complete society list in the first HTML response. They rely on JavaScript to render results or load more entries after a user action. A normal `requests.get()` call cannot click those buttons or wait for browser-rendered content.

The Bristol scraper uses Playwright for the listing page because the society directory has a load-more flow. The scraper:

1. Opens the Bristol groups page in a headless Chromium browser.
2. Waits for the first `a.group-box` society cards to appear.
3. Finds the load-more button.
4. Scrolls it into view.
5. Clicks it repeatedly while more societies are being added.
6. Waits for network activity to settle.
7. Passes the final rendered HTML into Beautiful Soup.

After Playwright has collected the complete list of Bristol society links, the individual detail pages are fetched with Requests and parsed with Beautiful Soup. This keeps browser automation limited to the part of the site where it is needed.

Manchester uses the same idea: Playwright is used to handle a dynamic activity list and the "see more" button. The script then parses the rendered HTML with Beautiful Soup.

## Handling Blockers

The main blocker in this project is dynamic content. When a page is rendered by JavaScript, the HTML returned by Requests may be incomplete or empty. In that case, Beautiful Soup has nothing useful to parse.

The workflow for handling that blocker is:

1. Try the simple path first with Requests and Beautiful Soup.
2. Inspect whether the expected container exists in the returned HTML.
3. If the content is missing because JavaScript is required, use Playwright.
4. Wait for stable selectors such as `a.group-box` or `div.list`.
5. Click load-more or see-more controls until all visible entries are loaded.
6. Pass `page.content()` to Beautiful Soup for normal parsing.

This keeps the scraper easy to understand while still supporting pages that require real browser behavior.

## Excel Output

All scrapers call `save_to_excel()` from `utils.py`. The exported spreadsheet includes:

- School
- Society Name
- President
- Email
- Society URL

The utility also formats the workbook with headers, alternating row fills, column widths, filters, frozen panes, and clickable hyperlinks for society URLs.