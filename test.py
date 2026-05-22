# Basic test file for inspecting what is returned from the browser. Confirm that the information is accurate before proceeding to extract and save to excel. If the DOM is not fully rendered, we'll get nothing, so at that point, I move to using playwright to use browser behaviour to get the page content for inspction before proceeding. Quite easy, really.

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv("TEST_LIST_URL")
School_name = os.getenv("TEST_SCHOOL_NAME")

page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

card = soup.find("div", id="groupResults")

group_results = soup.find("div", id="groupResults")
societies = group_results.find_all("div", class_="group-card")
for society in societies:
    a_tag = society.find("a")
    society_url = urljoin(URL, a_tag["href"])

    society_name = society.find("p", class_="accent").get_text(strip=True)

    society_page = requests.get(society_url)
    society_soup = BeautifulSoup(society_page.content, "html.parser")

    mail_div = society_soup.find("div", class_="socialmedia-c")
    email = "Not found"
    if mail_div:
        email_link = mail_div.find("a", class_="socemail")
        email = email_link["href"].replace("mailto:", "")

    print("Society:", society_name)
    print("Email:", email)
    print("URL:", society_url)
    print("=" * 60)
