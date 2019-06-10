import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import json
import time
from http.cookiejar import CookieJar

class MultiThreadScraper:

    def __init__(self, base_url):

        self.base_url = base_url.replace('www.','')
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=30)
        self.scraped_pages = set([])
        self.stored_pages = 0
        self.to_crawl = Queue()
        self.to_crawl.put(self.base_url)
        self.data = ({})

    def parse_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            if not ('?' in url or '#' in url or url.endswith('.xls') or url.endswith('.xlsx') or url.endswith('.doc') or url.endswith('.docx') or url.endswith('.pdf') or url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.png') or url.endswith('.ppt') or url.endswith('.css') or url.endswith('.js') or url.endswith('.mp4') or url.endswith('.zip') or url.endswith('.exe')):
                if url.startswith('/') or url.startswith(self.root_url):
                    url = urljoin(self.root_url, url)
                    if url not in self.scraped_pages:
                        self.to_crawl.put(url.replace('www.',''))
                elif 'uic.edu' in urlparse(url).netloc:
                    if url not in self.scraped_pages:
                        self.to_crawl.put(url.replace('www.',''))

    def scrape_info(self, html):
        self.stored_pages += 1
        return

    def post_scrape_callback(self, res):
        result = res.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)
            self.scrape_info(result.text)

    def scrape_page(self, url, c):
        try:
            res = requests.get(url, timeout=(3, 10))
            soup = BeautifulSoup(res.text, "lxml")
            for script in soup(['style','script','head','title','meta','[document]']):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_data = ' '.join(chunk for chunk in chunks if chunk)
            data = ({
                'url': url,
                'text':text_data
                })
            with open('data/'+str(c)+'.json','w') as outfile:
                json.dump(data, outfile)
            return res
        #except requests.RequestException:
        except Exception as e:
            return

    def run_scraper(self):
        c = 0
        while c < 3000:
            try:
                target_url = self.to_crawl.get(timeout=10)
                if target_url not in self.scraped_pages:
                    c += 1
                    print("Scraping URL: {}".format(target_url))
                    self.scraped_pages.add(target_url)
                    job = self.pool.submit(self.scrape_page, target_url, c)
                    job.add_done_callback(self.post_scrape_callback)
                    
            except Empty:
                return
            except Exception as e:
                print(e)
                continue
        print(c)
        

if __name__ == '__main__':
    s = MultiThreadScraper("https://www.cs.uic.edu/")
    start = time.time()
    s.run_scraper()
    end = time.time()
    print(end-start)