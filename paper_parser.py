import json

import requests
from bs4 import BeautifulSoup
from urllib3.util import Retry


class PaperParser:

    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': 'Google Chrome;v=113, Chromium;v=113, Not-A.Brand;v=24',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'macOS',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        
        self.cookies = {
            'nginx-cloud-site-id': 'mssp-us-1',
            'privacy-policy': '1,XXXXXXXXXXXXXXXXXXXXXX',
            'test_cookie': 'seg%3D12759785'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookies)
        
        self.retry = Retry(total=5,
                           read=5,
                           connect=5,
                           backoff_factor=0.3,
                           status_forcelist=(500, 502, 504))
        
        self.adapter = requests.adapters.HTTPAdapter(max_retries=self.retry, 
                                                     pool_connections=100, 
                                                     pool_maxsize=100)
        self.session.mount('http://', self.adapter)
        self.session.mount('https://', self.adapter)


    def scrape_abstract(self, DOI):
        abstract = 'Not Available'
        
        try:
            response = self.session.get(url=f"https://doi.org/{DOI}",
                                        timeout=(3.05, 10))

            soup = BeautifulSoup(response.content, "html5lib")
            
            if "springer" in response.url:
                abstract = soup.find('div', class_='c-article-section__content').text.strip()
                # soup.find('div', id='Abs1-content').text
            
            if "ieee" in response.url:
                abstract = soup.find('meta', {'property': 'og:description'})['content'].strip()

            if "acm" in response.url:
                abstract = soup.find('div', class_='abstractSection').text.strip()
        except Exception as e:
            print(f"Abstract scraping failed due to: {e}")
            abstract = 'Not Available'
            
        return abstract


    def fetch_info_semanticscholar(self, DOI):   
        response = self.session.get(f"https://api.semanticscholar.org/v1/paper/{DOI}")
        status_code, content = (response.status_code, json.loads(response.content))     
        
        title = content.get('title', 'Not Available')
        
        authors = ", ".join([author.get('name') for author in content.get('authors', [])])

        doi = content.get('doi', 'Not Available')

        url = self.session.get(f"https://doi.org/{DOI}", allow_redirects=True).url

        venue = content.get('venue', 'Not Available')

        year = content.get('year', 'Not Available')

        fieldsOfStudy = ", ".join(content.get('fieldsOfStudy', []))

        topics = ", ".join([topic.get('topic') for topic in content.get('topics', 'Not Available')])

        abstract = content.get('abstract', self.scrape_abstract(DOI))
        
        result = dict(title=title, 
                    authors=authors,
                    doi=doi,
                    url=url,
                    venue=venue,
                    year=year, 
                    fieldsOfStudy=fieldsOfStudy,
                    topics=topics,
                    abstract=abstract)
        
        return (status_code, result)


    def fetch_info_crossref(self, DOI):
        response = self.session.get(f'https://api.crossref.org/works/{DOI}')
        status_code, content = (response.status_code, json.loads(response.content))

        title = "".join(content.get('message').get('title', "Not Available"))

        authors = ", ".join([author.get('given')+' '+author.get('family')
                             for author in content.get('message').get('author', [])])

        doi = content.get('message').get('DOI', "Not Available")
        
        url = self.session.get(f"https://doi.org/{DOI}", allow_redirects=True).url

        venue = "".join(content.get('message').get('short-container-title', "Not Available"))

        year = content.get('message').get('published-print').get('date-parts', "Not Available")[0][0]

        topics = content.get('message').get('link')[0].get('intended-application')

        abstract = content.get('message').get('abstract', self.scrape_abstract(DOI))

        result = dict(title=title,
                    authors=authors,
                    doi=doi,
                    url=url,
                    venue=venue,
                    year=year,
                    fieldsOfStudy="Not Available",
                    topics=topics,
                    abstract=abstract)
        return (status_code, result)


    def parse_doi(self, DOI):
        try:
            print(f"Parsing for DOI (crossref): {DOI}", end=" =====> ")

            status_code, result = self.fetch_info_crossref(DOI)
    
            if status_code == 200:
                print(f"[{status_code}:successful]")
            else:
                print([f"{status_code}:failed"])
        
        except:
            print(f"Parsing for DOI (semanticscholar): {DOI}", end=" =====> ")
            
            status_code, result = self.fetch_info_semanticscholar(DOI)

            if status_code == 200:
                print(f"[{status_code}:successful]")
            else:
                print([f"{status_code}:failed"])
        
        return status_code, result
    
    
    # https://orcid.org/works/resolve/doi?value=10.1109/TASC.2010.2088091