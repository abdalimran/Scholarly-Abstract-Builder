import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pickle
import time

class DBLPParser:
    
    def __init__(self):
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
                       "Accept-Encoding":"gzip, deflate", 
                       "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
                       "DNT":"1",
                       "Connection":"close", 
                       "Upgrade-Insecure-Requests":"1"}

        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path='./webdriver/chromedriver', options=self.chrome_options)
    
    
    def proceedings_info(self, paper_dois):
        result = dict(title = paper_dois.find('span', {'class':'title'}).text,
                      authors = ", ".join([author.text for author in paper_dois.find_all('span', {'itemprop':'name'})[:-1]]),
                      publisher = paper_dois.find('span', {'itemprop':'publisher'}).text,
                      datePublished = paper_dois.find('span', {'itemprop':'datePublished'}).text,
                      isbn = paper_dois.find('span', {'itemprop':'isbn'}).text \
                      if (paper_dois.find('span', {'itemprop':'isbn'})) != None else "-")
        return result
    
    
    def fetch_info(self, soup, no_track=False):
        if no_track==True:
            paper_dois = soup.find_all('ul', attrs={'class': 'publ-list'})
            result = {'proceedings_info': self.proceedings_info(soup.find('li', attrs={'class':'entry editor'})\
                                                                .find_next('cite', attrs={'class':'data'}))}
            for p in paper_dois:
                result['research'] = set(re.search(r'(?<=doi\.org\/)(.*)',link['href']).group(0) \
                                         for link in p.find_all('a', {'href': re.compile(r'doi\.org/')}))
        else:
            tracks = soup.find_all('h2')
            paper_dois = soup.find_all('ul', attrs={'class': 'publ-list'})
            result = {'proceedings_info': self.proceedings_info(paper_dois.pop(0))}
            if len(tracks)==len(paper_dois):
                for t, p in zip(tracks, paper_dois):
                    result[t.text] = set(re.search(r'(?<=doi\.org\/)(.*)',link['href']).group(0) \
                                         for link in p.find_all('a', {'href': re.compile(r'doi\.org/')}))
            else:
                print("Missmatch in track and article length!")
        return result
    
    
    def parse_proceedings(self, DBLP_LINK, no_track=False):
        response = requests.get(DBLP_LINK, headers=self.headers)
        if response.status_code == 200:
            content = response.content
            soup = BeautifulSoup(content, "html5lib")
            result = self.fetch_info(soup, no_track=no_track)
        else:
            print("[%s] Error while parsing!"%response.status_code)
            result = None
        return result


    def parse_for_query(self, DBLP_LINK):
      self.driver.get(DBLP_LINK)
      lastHeight = self.driver.execute_script("return document.body.scrollHeight")
      
      while True:
          self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
          time.sleep(0.5)
          newHeight = self.driver.execute_script("return document.body.scrollHeight")
          if newHeight == lastHeight:
              break
          lastHeight = newHeight
      
      result = {'proceedings_info': dict(title = DBLP_LINK.partition("search?q=")[2].replace("%20"," "),
                                         authors = "",
                                         publisher = "",
                                         datePublished = "",
                                         isbn = "")}
      
      soup = BeautifulSoup(self.driver.page_source, "html5lib")
      paper_dois = soup.find_all('ul', attrs={'class': 'publ-list'})
      
      result['research'] = set(re.search(r'(?<=doi\.org\/)(.*)',link['href']).group(0)\
                               for link in paper_dois[0].find_all('a', {'href': re.compile(r'doi\.org/')}))
      
      return result