# Federal Reserve Account Scraper

## Setup
- Ensure you have python3 installed
- `cd` to the project directory
- run `make setup`
- Accounts scraped are stored in `federal-reserves-accounts.csv`

## Tools
- venv (venv folder is called `fda-scraper`)
- BeautifulSoup
- requests-futures

## Usage

### `make run`
Runs the `run.sh` script which runs `scrap.py` to either:
- Get all accounts if no existing record is found
- Get all accounts since the latest record found in `federal-reserves-accounts.csv`

## Note
- Remember to activate the venv `. fda-scraper/bin/activate` if developing or running the python files directly
