## Sneaker Scraper

Scrapes StockX (currently) for prices and recent trends.

### USAGE

source venv/bin/activate
pip install -r requirements.txt
casperjs browse.js --search=adidas
python3 scraper.py

### OUTPUT

Pandas dataframe with columns that show shoe size and lowest available price

### TOOLS

CasperJS for browser automation
Beautifulsoup and Pandas to search webpage for relevant information

CURRENTLY WIP - improving parser (for more sites) and replacing unnecessary CasperJS with Selenium
-requires Selenium Chrome webdriver in path - https://sites.google.com/a/chromium.org/chromedriver/downloads