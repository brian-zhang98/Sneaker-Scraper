from bs4 import BeautifulSoup
from selenium import webdriver
import re
import sys
import time

#TO-DO: GOAT AUTOMATION DETECTION (also goat has a different url after you click for available sizes), ADD STADIUMGGOODS TO SITES SCRAPABLE, figure out flightclub $cad and size
#site: search url, product url, anything else that needs to be at the end of url
SITES_TO_PARSE = {
	'stockx': ['/search?s=', '/', ''],
	'goat': ['/search?query=', '/sneakers/', 'available-sizes'],
	'flightclub': ['/catalogsearch/result/?q=', '/', '?size={}']
}

class SneakerParser:
	def __init__(self, input_product, size, site_to_parse):
		self.product = input_product
		self.size = size
		self.site = site_to_parse
		self.url = 'https://' + self.site + '.com' + SITES_TO_PARSE[self.site][1] + self.product.replace(' ', '-') + SITES_TO_PARSE[self.site][2].format(self.size)
		self.html = None
		self.soup = None
		self.price = None
		self.search_results={}

	def get_html(self):
		driver = webdriver.Chrome()
		driver.get(self.url)
		time.sleep(5)
		self.html=driver.page_source
		self.soup = BeautifulSoup(self.html, 'lxml')
		driver.close()
		
	def is_product_page(self):
		#StockX has this on its 404 not found page
		#if(self.soup.find('div', class_ = 'not-found-title') is not None):

		#404.. is 404 followed by 2 wildcards to avoid finding a $404 price or something similar, should work for all sites
		if(self.soup.find(string=re.compile('404..')) is not None or self.soup.find(string='SKU: ') is not None):
			return False
		return True

	def get_set_price(self):
		#stockx
		if(self.site == list(SITES_TO_PARSE.keys())[0]):
			divs = self.soup.find_all('div', class_ = 'title', string=self.size)
			for div in divs:
				if('$' in div.find_next_sibling('div').get_text()):
					self.price = div.find_next_sibling('div').get_text()
			print(self.price)
		#goat
		elif(self.site == list(SITES_TO_PARSE.keys())[1]):
			print('price')
			pass
		#flightclub
		elif(self.site == list(SITES_TO_PARSE.keys())[2]):
			driver = webdriver.Chrome()
			driver.get(self.url)
			time.sleep(5)
			self.html = driver.page_source
			self.soup = BeautifulSoup(self.html, 'lxml')
			cdn = self.soup.find('a', attrs={'title': re.compile('https://www.flightclub.com/directory/currency/switch/currency/CAD/')})['href']
			time.sleep(5)
			driver.get(cdn)
			time.sleep(5)
			self.html = driver.page_source
			self.soup = BeautifulSoup(self.html, 'lxml')
			buttons = self.soup.find_all('button', class_ = re.compile('attribute-button-text '))
			for button in buttons:
				if(button.get_text().replace('"', '').strip() == self.size):
					id = button['id']
			driver.find_element_by_id(id).click()
			time.sleep(5)
			self.html = driver.page_source
			self.soup = BeautifulSoup(self.html, 'lxml')

			self.price = self.soup.find('span', class_ = 'regular-price').find('span', class_='price', string = re.compile('\$')).get_text()
			print(self.price)

	def update_search_url(self):
		self.url = 'https://' + self.site + '.com' + SITES_TO_PARSE[self.site][0] + self.product.replace(' ', '%20')

	def get_search_results(self):
		#stockx
		if(self.site == list(SITES_TO_PARSE.keys())[0]):
			for result in self.soup.find_all('a', class_ = 'tile-link'):
				self.search_results[result.find_next('h4').get_text().lower()] = result['href']
		#goat
		elif(self.site == list(SITES_TO_PARSE.keys())[1]):
			for result in self.soup.find_all('a', class_ = 'cell', attrs={'data-qa': 'search_grid_cell'}):
				self.search_results[result.find_next('div', class_='grid-cell--name').find_next('p').get_text().lower()] = result['href']
		#flightclub - href is full link, shoe names are wack
		elif(self.site == list(SITES_TO_PARSE.keys())[2]):
			for result in self.soup.find_all('a', class_ = 'result algolia-clearfix'):
				shoe = result['href'].split('/')[-1].replace('-', ' ').lower()
				#self.search_results[result.find_next('p', class_='result-title text-ellipsis').get_text().lower()] = result['href']
				self.search_results[shoe] = '/' + result['href'].split('/')[-1]

	#show search results, make sure to give an option to back out and try and re-search, also remember to change self.url here
	def display_search_results(self):
		count = 1;
		print('Displaying {} results:'.format(len(self.search_results)))
		for shoe in self.search_results:
			print(str(count) + '. ' + shoe)
			count += 1

	def prompt_for_shoe_from_results(self):
		while(True):
			sys.stdout.write('Please choose a shoe from the results either with its corresponding # or its full name. Please enter -1 to enter a new search string.\n')
			input_shoe = input().lower()
			if(input_shoe == '-1'):
				return False
			elif(input_shoe.isdigit() and int(input_shoe) <= len(self.search_results.keys()) and int(input_shoe) != 0):
				self.url = 'https://' + self.site + '.com' + SITES_TO_PARSE[self.site][1] + self.search_results[list(self.search_results.keys())[int(input_shoe)-1]] + SITES_TO_PARSE[self.site][2].format(self.size)
				return True
			elif(input_shoe in self.search_results.keys()):
				self.url = 'https://' + self.site + '.com' + SITES_TO_PARSE[self.site][1] + self.search_results[input_shoe] + SITES_TO_PARSE[self.site][2].format(self.size)
				return True

	def put_to_db(self):
		pass

if __name__ == '__main__':
	while(True):
		sys.stdout.write('What shoe are you looking for?\n')
		shoe = input()
		sys.stdout.write('What size are you?\n')
		size = input()
		#parser = SneakerParser('Adidas Yeezy Boost 350 V2 Static Reflective', '9.5', 'stockx')
		parser = SneakerParser(shoe, size, 'flightclub')
		parser.get_html()
		#print(parser.html)
		if(parser.is_product_page()):
			parser.get_set_price()
		else:
			parser.update_search_url()
			#time.sleep(10)
			parser.get_html()
			parser.get_search_results()
			parser.display_search_results()
			if(parser.prompt_for_shoe_from_results()):
				parser.get_html()
				parser.get_set_price()
				break