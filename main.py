import requests, argparse, json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, base_url, keywords, max_pages, filename=''):
        self.base_url = base_url
        self.keywords = keywords
        self.max_pages = max_pages
        self.visited_urls = set()
        self.urls = set()
        self.matched_urls = {}
        self.should_save = False if filename=='' or filename is None else True
        self.filename = f'{filename}.json'


    def find_keywords(self, text):
        matched_keywords = []

        for keyword in self.keywords:
            if (keyword.lower() in text.lower()):
                matched_keywords.append(keyword)
        
        if(len(matched_keywords)):
            self.matched_urls[self.base_url] = matched_keywords


    def print_results(self):
        for link, keywords in self.matched_urls.items():
            print(f'Znaleziono {keywords} w: {link}')


    def save_results(self):
        if(not self.should_save):
            return
        
        with open(self.filename, 'w') as file:
            file.write(json.dumps(self.matched_urls, indent=4))
        print(f'Zapisano wyniki do {self.filename}')


    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)


    def run(self):
        for i in range(self.max_pages):
            try:
                response = requests.get(self.base_url)
                if response.status_code != 200:
                    continue
                
                self.visited_urls.add(self.base_url)
                print(f'[{i+1}/{self.max_pages}] Przeszukiwanie: {self.base_url}')

                soup = BeautifulSoup(response.content, features='html.parser')
                
                for a_tag in soup.find_all('a', href=True):
                    link = urljoin(self.base_url, a_tag['href'])
                    if(link not in self.urls and link not in self.visited_urls):
                        if(self.is_valid_url(link)):
                            self.urls.add(link)

                self.find_keywords(soup.getText())

                if(len(self.urls)==0):
                    break
                
                self.base_url = self.urls.pop()

            except Exception as e:
                print(e)
                self.print_results()
                self.save_results()

        self.print_results()
        self.save_results()
        return self.matched_urls
    

# Przykład uruchomienia
# python main.py --link https://books.toscrape.com/catalogue/page-1.html --keywords world adventure --pages 50 --save wyniki

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--link', default='https://books.toscrape.com/catalogue/page-1.html', type=str,
                        help="Link do punktu początkowego")
    parser.add_argument('--keywords', default=['python'], nargs='*', type=str,
                        help="Słowa kluczowe których program będzie szukał")
    parser.add_argument('--pages', default=1, type=int, 
                        help="Maksymalna liczba odwiedzonych stron")
    parser.add_argument('--save', type=str, help="Nazwa pliku do którego zostaną zapisane wyniki")

    args = parser.parse_args()
    
    if(args.save):
        if((i := args.save.find('.')) != -1):
            args.save = args.save[:i]

    crawler = Crawler(args.link, args.keywords, args.pages, args.save)
    results = crawler.run()

