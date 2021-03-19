import os
import csv
import re
import time
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession
from models.fy import FY
from models.quarter import Quarter
from models.text import Text
from models.account import Account
from datetime import datetime
from pprint import pprint

scrap_date_format = "%B %d, %Y"
save_date_format = "%d %b %Y"

savefile_name = "federal-reserves-accounts.csv"
csv_filepath = os.path.join(".", savefile_name)

fda_domain = "https://fsapps.fiscal.treasury.gov"
fda_issues_link = f"{fda_domain}/dts/issues/collapsed"

keyword = "Federal Reserve Account"

session = FuturesSession(max_workers=30)


def main():
    print("Starting")
    start_time = time.time()
    create_savefile_if_not_exists()

    record = get_latest_scraped_record()

    latest_quarter = None
    latest_scrap_date = None

    if record:
        latest_quarter = record[1]
        latest_scrap_date = record[2]
        print(
            f"Latest record: FY{record[0]} Q{record[1]} {record[2].strftime(save_date_format)} ${record[3]}"
        )
    else:
        print(f"No record found, will attempt to scrap all text files for accounts")

    print("Getting issues page")
    r = session.get(fda_issues_link).result()

    html_soup = BeautifulSoup(r.text, features="html.parser")

    print("Getting all FYs or since latest")
    fys = get_fys(html_soup, latest_scrap_date)

    print("Getting all quarters or since latest")
    quarters = get_quarters(fys, latest_scrap_date, latest_quarter)

    texts = get_texts(quarters, latest_scrap_date)

    if not texts:
        print("No new text file found")
    else:
        print(f"Downloading {len(texts)} text files")
        accounts = get_accounts(texts)

        save_accounts(accounts)

    seconds_taken = time.time() - start_time
    print(f"Finished in {round(seconds_taken)}s")


def create_savefile_if_not_exists():
    if not os.path.exists(csv_filepath):
        print(f"Creating csv savefile: {savefile_name}")
        with open(csv_filepath, "w"):
            pass


def get_latest_scraped_record():
    with open(csv_filepath, "rb") as f:
        # assume that length of last line is not more than 100 chars
        try:
            f.seek(-100, os.SEEK_END)
        except OSError:
            if sum(1 for line in f) < 1:
                return None
            f.seek(0)

        last_line = f.readlines()[-1].decode()
        reader = csv.reader([last_line], delimiter=",")
        values = list(reader)[0]
        latest_scrapped_date = datetime.strptime(values[2], save_date_format)
        return (values[0], values[1], latest_scrapped_date, values[3])


def get_fys(html_soup, since=None):
    fy_soups = html_soup.select(".plus-circle-yellow-icon")
    fys = [
        FY(fy["id"], int(fy["id"][2:]), f'{fda_domain}{fy["href"]}') for fy in fy_soups
    ]

    if since:
        fys = [fy for fy in fys if fy.year >= since.year]

    for fy in fys:
        fy.futureRes = session.get(fy.url)

    return fys


def get_quarters(fys, since=None, since_quarter=None):
    quarters = []
    for fy in fys:
        if since and fy.year < since.year:
            continue
        fy.res = fy.futureRes.result()
        fy_soup = BeautifulSoup(fy.res.content, features="html.parser")
        fy_quarters = [
            Quarter(
                fy,
                quarter_a_tag["id"],
                quarter_a_tag.text[-1],
                f'{fda_domain}{quarter_a_tag["href"]}',
            )
            for quarter_a_tag in fy_soup.find(id=fy.id).parent.select("a.bold")
        ]

        if since and fy.year == since.year:
            fy_quarters = [
                fy_quarter
                for fy_quarter in fy_quarters
                if fy_quarter.quarter >= since_quarter
            ]

        for fy_quarter in fy_quarters:
            fy_quarter.futureRes = session.get(fy_quarter.url)
        quarters.extend(fy_quarters)

    return quarters


def get_texts(quarters, since=None):
    texts = []
    for quarter in quarters:
        quarter.res = quarter.futureRes.result()
        quarter_soup = BeautifulSoup(quarter.res.content, features="html.parser")
        a_tags = [
            a_tag
            for a_tag in quarter_soup.find(id=quarter.id).parent.select(
                'ul[data-margin^="top-small"] a'
            )
            if a_tag.text == "TEXT"
        ]

        for a_tag in a_tags:
            date = datetime.strptime(
                a_tag.parent.parent.find("span").text, scrap_date_format
            )
            if since and date <= since:
                continue
            texts.append(Text(quarter, date, f'{fda_domain}{a_tag["href"]}'))

    for text in texts:
        text.futureRes = session.get(text.url)

    return texts


def get_accounts(texts):
    accounts = []
    for text in texts:
        text.res = text.futureRes.result()

        content = None
        try:
            content = text.res.content.decode("utf-8", "ignore")
        except UnicodeDecodeError:
            print(
                f"Error decoding for {text.quarter.fy.id}, Q{text.quarter.quarter}, {text.date}"
            )
            continue

        # extracting the values of the `keyword` from content
        # e.g. Federal Reserve Account                $  1,728,569 $  1,613,514 $  1,622,986 $   1,781,679

        keyword_index = content.find(keyword)
        if keyword_index == -1:
            print(
                f"Error getting account for {text.quarter.fy.id}, Q{text.quarter.quarter}, {text.date}: Could not find '{keyword}' in file"
            )
            continue

        start = keyword_index + len(keyword)
        start = content.find("$", start) + 1
        end = content.find("\n", start)
        values = content[start:end].strip()
        account_value = values[: values.find(" ")]
        account_value = re.sub("[^0-9]", "", account_value)

        accounts.append(Account(text, account_value))

    return sorted(accounts)


def save_accounts(accounts):
    with open(csv_filepath, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")

        for account in accounts:
            writer.writerow(
                [
                    account.text.quarter.fy.year,
                    account.text.quarter.quarter,
                    account.text.date.strftime(save_date_format),
                    account.value,
                ]
            )


if __name__ == "__main__":
    main()
