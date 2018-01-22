import sys
import pandas as pd
import subprocess
from bs4 import BeautifulSoup, Comment
import os

class StockXParser(object):
    def __init__(self, html_path):
        self.input_html = None
        self.soup = None

        self.load_input_html(html_path)

    def load_input_html(self, html_path):
        with open(html_path, 'r') as f:
            self.input_html = f
            self.soup = BeautifulSoup(f, 'lxml')

    def is_search_results(self):
        if (self.soup.find("div", class_ = "result-tile") != None):
            return True
        else:
            return False

    def query_yes_no(self, question, default="yes"):
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    def handle_search_results(self):
        results = self.soup.findAll("div", class_ = "result-tile")
        str_results = []
        self.query_yes_no("Display all {} results of your search?".format(len(results)))

        for result in results:
            comments = result.findAll(text=lambda text: isinstance(text, Comment))

            for comment in comments:
                comment.extract()

            for br in result.findAll('br'):
                br.replace_with(' ')

            print(result.findAll("h4")[0].text.replace('<h4>', '').replace('<\h4>', ''))

            str_results.append(result.findAll("h4")[0].text.replace('<h4>', '').replace('<\h4>', '').lower())

        print("Which sneaker would you like to receive prices for?")
        choice = input().lower()
        while(choice not in str_results):
            print("Sneaker not found in search results. Please try again.")
            choice = input().lower()

        return choice

    def scrape_product_page(self):
        size_price_dict = {}
        div = self.soup.find("div", class_="select-options")
        for size in div.findAll("div", class_ = "title"):
            size_price_dict[size.get_text()] = size.next_sibling.get_text()

        df = pd.DataFrame.from_dict(size_price_dict, 'index')
        df.columns=['PRICE']
        print(df)

        trend = self.soup.find("div", class_="dollar").get_text()
        percent = self.soup.find("div", class_="percentage").get_text()

        print(("Recent trend: {}, {}").format(trend, percent))

def runCasperJS(search):
    APP_ROOT = os.path.dirname(os.path.realpath(__file__))
    CASPERJS = [r'C:\casperjs-1.1.4-1\bin\casperjs.exe']
    SEARCH = '"""--search={}"""'.format(search)
    SCRIPT = os.path.join(APP_ROOT, 'browse.js')
    params = [CASPERJS, SCRIPT, SEARCH]
    child = subprocess.Popen(params, shell=True, stderr=subprocess.PIPE)
    while True:
        out = child.stderr.read(1)
        return out
        if out == '' and child.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()
            return out

if __name__ == '__main__':
    input_html = './page.html'

    sxParser = StockXParser(input_html)

    if(sxParser.is_search_results()):
        search = sxParser.handle_search_results()
        runCasperJS(search)
        sxParser = StockXParser(input_html)

    sxParser.scrape_product_page()