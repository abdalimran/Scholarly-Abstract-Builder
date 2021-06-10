import requests
from requests.packages.urllib3.util.retry import Retry
import json
import pickle

class PaperParser:

    def __init__(self):
        self.session = requests.Session()
        self.retry = Retry(total=5,
                            read=5,
                            connect=5,
                            backoff_factor=0.3,
                            status_forcelist=(500, 502, 504))
        self.adapter = requests.adapters.HTTPAdapter(max_retries=self.retry, pool_connections=100, pool_maxsize=100)
        self.session.mount('http://', self.adapter)
        self.session.mount('https://', self.adapter)


    def fetch_info(self, content, DOI):
        result = dict(title = content['title'],
                    authors = ", ".join([author['name'] for author in content['authors']]),
                    doi = content['doi'],
                    url = self.session.get("https://doi.org/%s"%DOI, allow_redirects=True).url,
                    venue = content['venue'],
                    year = content['year'],
                    fieldsOfStudy = ", ".join(content['fieldsOfStudy']) if content['fieldsOfStudy']!=None else "No Fields of Study Found",
                    topics = ", ".join([topic['topic'] for topic in content['topics']]),
                    abstract = content['abstract'] if content['abstract']!=None else "No Abstract Found")
        return result


    def fetch_info_crossref(self, content, DOI, has_abstract=False):
        if has_abstract == False:
            result = dict(title = content['message']['title'][0],
                        authors = ", ".join([author['given']+' '+author['family'] for author in content['message']['author']]),
                        doi = content['message']['DOI'],
                        url = self.session.get("https://doi.org/%s"%DOI, allow_redirects=True).url,
                        venue = content['message']['short-container-title'][0] if len(content['message']['short-container-title'])!=0 else '-',
                        year = content['message']['published-print']['date-parts'][0][0],
                        fieldsOfStudy = "Not Available",
                        topics = content['message']['link'][0]['intended-application'],
                        abstract = "No Abstract Found")
        else:
            result = dict(title = content['message']['items'][0]['title'][0],
                        authors = ", ".join([author['given']+' '+author['family'] for author in content['message']['items'][0]['author']]),
                        doi = content['message']['items'][0]['DOI'],
                        url = self.session.get("https://doi.org/%s"%DOI, allow_redirects=True).url,
                        venue = content['message']['items'][0]['short-container-title'][0],
                        year = content['message']['items'][0]['published-print']['date-parts'][0][0],
                        fieldsOfStudy = "Not Available",
                        topics = content['message']['items'][0]['link'][0]['intended-application'],
                        abstract = content['message']['items'][0]['abstract'])
        return result


    def parse_doi(self, DOI):
        print("Parsing for DOI: %s"%DOI, end=" =====> ")
        response = self.session.get("https://api.semanticscholar.org/v1/paper/%s"%DOI)
        status_code, content = (response.status_code, json.loads(response.content))
        
        if status_code == 200:
            result = (status_code, self.fetch_info(content, DOI))
            print("[%s:successful]"%status_code)
        else:
            print(["%s:failed"%status_code])
            print("Trying through crossref", end=" =====> ")
            response = self.session.get('https://api.crossref.org/works?filter=doi:%s,has-abstract:true'%DOI)
            status_code, content = (response.status_code, json.loads(response.content))
            
            if status_code == 200 and len(content['message']['items'])!=0:
                result = (status_code, self.fetch_info_crossref(content, DOI, has_abstract=True))
                print("[%s:successful, FOUND WITH ABSTRACT]"%status_code)
            elif status_code == 200 and len(content['message']['items'])==0:
                response = self.session.get('https://api.crossref.org/works/%s'%DOI)
                status_code, content = (response.status_code, json.loads(response.content))
                result = (status_code, self.fetch_info_crossref(content, DOI, has_abstract=False))
                print("[%s:successful, FOUND METADATA ONLY]"%status_code)
            else:
                print("[%s:failed]"%status_code)
                result = (status_code, None)
        return result