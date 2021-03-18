from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import os
import csv

# create and open file to check and store latest account value
csv_filepath = os.path.join(".", "federal-reserves-accounts.csv")
if not os.path.exists(csv_filepath):
    with open(csv_filepath, "w"):
        pass


def check_latest_scrapped(csv_filepath, latest_issue_date):
    with open(csv_filepath, "rb") as f:
        # assume that length of last line is not more than 50 chars
        try:
            f.seek(-50, os.SEEK_END)
        except OSError:
            if sum(1 for line in f) < 1:
                return
            f.seek(0)

        last_line = f.readlines()[-1].decode()
        reader = csv.reader(last_line, delimiter=",")
        latest_scrapped_date = datetime.strptime(list(reader)[0][0], date_format)
        if latest_scrapped_date >= latest_issue_date:
            print(
                f"latest scrapped issue: {latest_scrapped_date.strftime(date_format)}"
            )
            exit(0)


# getting the latest issue text
fda_domain = "https://fsapps.fiscal.treasury.gov"

fda_issues_link = f"{fda_domain}/dts/issues"

r = requests.get(fda_issues_link)

html_soup = BeautifulSoup(r.text, features="html.parser")

main_soup = html_soup.find("main")

latest_fy_soup = main_soup.find_all("h-box")[2]

latest_quarter_soup = latest_fy_soup.select('div[data-margin^="top-small"]')[-1]

latest_issue_soup = latest_quarter_soup.select('ul[data-margin^="top-small"]')[0]

date_format = "%B %d, %Y"

latest_issue_date = latest_issue_soup.find("span").text
latest_issue_date = datetime.strptime(latest_issue_date, "%B %d, %Y")

print(f"latest issue date found: {latest_issue_date.strftime(date_format)}")

check_latest_scrapped(csv_filepath, latest_issue_date)

# text is middle
latest_issue_text_link_path = latest_issue_soup.find_all("a")[1]["href"]

latest_issue_text_link = f"{fda_domain}/{latest_issue_text_link_path}"

latest_issue_text = requests.get(latest_issue_text_link).text

keyword = "Total Federal Reserve Account"

# extracting the values of the `keyword` from latest_issue_text
# e.g. 128,227     1,248,478    11,614,695

start = latest_issue_text.find(keyword) + len(keyword)
end = latest_issue_text.find("\n", start)
values = latest_issue_text[start:end].strip()
account_value = values[: values.find(" ")]
account_value = re.sub("[^0-9]", "", account_value)

with open(csv_filepath, "a") as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerow([latest_issue_date.strftime(date_format), account_value])
