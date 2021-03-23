import argparse
from bs4 import BeautifulSoup
import re
import csv
import requests
from typing import List


PREFIX = "https://www.thesaigontimes.vn"


class ExportCSV:
    def __init__(self, url: str, title: str, author: str, time: str):
        self.url: str = url
        self.title: str = title
        self.author: str = author
        self.time: str = time

    def write_to_csv(self) -> List[str]:
        return [self.url, self.title, self.author, self.time]


def helper() -> argparse.ArgumentParser:
    """CLI helper function"""

    parser = argparse.ArgumentParser(
        description="Mini Crawler Pre-work for 'thesaigontimes.vn'."
    )
    parser.add_argument(
        "--url", type=str, help="url of thesaigontimes.vn", required=True
    )

    return parser


def validate_url(url: str):
    """Validate url input"""

    if "thesaigontimes.vn" not in url:
        raise ValueError("url must from thesaigontimes.vn!")

    return


def get_urls(url: str) -> List[ExportCSV]:
    """Get urls from url input"""

    urls = []
    list_csv = []

    resp = requests.get(url)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "lxml")
        filtered_href = soup.find_all("a")

        first_url = parse_data(url, soup)
        if first_url:
            list_csv.append(first_url)

        # parse all "a" tag in filtered_href
        for parser in filtered_href:
            uri = parser.get("href")
            if uri and re.search(r"/(td|\d)\d*/(.*?).html", uri):
                urls.append(f"{PREFIX}{uri}")
    urls = list(set(urls))
    if urls:
        for url in urls:
            data = parse_data(url)
            if data:
                list_csv.append(data)

    return list_csv


def parse_data(url: str, soup: BeautifulSoup = None) -> ExportCSV:
    """Parse data from url"""

    c = ExportCSV(url, str, str, str)

    if soup is None:
        resp = requests.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
        else:
            return

    # parse title
    title = soup.find("span", {"id": "ctl00_cphContent_lblTitleHtml"})
    if title:
        c.title = str(title.text)
    else:
        c.title = str(soup.title.text)

    # parse author
    author = soup.find("span", {"id": "ctl00_cphContent_Lbl_Author"})
    if author:
        c.author = str(author.text).split("(*)")[0]
    else:
        author = soup.find("span", {"class": "ReferenceSource"})
        c.author = str(author.text)

    # parse time
    time = soup.find("span", {"id": "ctl00_cphContent_lblCreateDate"})
    if time is None:
        time = soup.find(
            "span", {"id": "ctl00_uscSearchAndVNKeyBoard_lblDate"})
    c.time = "".join(str(time.text).split(",")[1:])

    return c


def write_csv(list_csv: List[ExportCSV]):
    """Write list_csv to file"""

    if list_csv:
        with open("data.csv", "w", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["URL", "Title", "Author", "Date"])

            for c in list_csv:
                writer.writerow(c.write_to_csv())


if __name__ == "__main__":
    try:
        parser = helper().parse_args()
        url = parser.url
        validate_url(url)
    except ValueError as e:
        print(f"error: {e}")
    else:
        print("info: processing...")
        list_csv = get_urls(url)
        write_csv(list_csv)
        print("info: done.")
