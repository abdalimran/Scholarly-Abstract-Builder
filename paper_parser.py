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
        try: title=content['title'];
        except: title='Not Available';

        try: authors=", ".join([author['name'] for author in content['authors']]);
        except: authors='Not Available';

        try: doi=content['doi'];
        except: doi='Not Available';

        try: url=self.session.get("https://doi.org/%s"%DOI, allow_redirects=True).url;
        except: url='Not Available';

        try: venue=content['venue'];
        except: venue='Not Available';

        try: year=content['year'];
        except: year='Not Available';

        try: fieldsOfStudy=", ".join(content['fieldsOfStudy']);
        except: fieldsOfStudy='Not Available';

        try: topics=", ".join([topic['topic'] for topic in content['topics']]);
        except: topics='Not Available';

        try: abstract=content['abstract'];
        except: abstract='Not Available';
        
        result = dict(title=title, 
                    authors=authors,
                    doi=doi,
                    url=url,
                    venue=venue,
                    year=year, 
                    fieldsOfStudy=fieldsOfStudy,
                    topics=topics,
                    abstract=abstract)
        
        return result


    def fetch_info_crossref(self, content, DOI, has_abstract=False):
        if has_abstract == False:
            try: title=content['message']['title'][0];
            except: title='Not Available';

            try: authors=", ".join([author['given']+' '+author['family'] for author in content['message']['author']]);
            except: authors='Not Available';

            try: doi=content['message']['DOI'];
            except: doi='Not Available';

            try: url=self.session.get("https://doi.org/%s"%DOI, allow_redirects=True).url;
            except: url='Not Available';

            try: venue=content['message']['short-container-title'][0];
            except: venue='Not Available';

            try: year=content['message']['published-print']['date-parts'][0][0];
            except: year='Not Available';

            try: topics=content['message']['link'][0]['intended-application'];
            except: topics='Not Available';

            result = dict(title=title,
                        authors=authors,
                        doi=doi,
                        url=url,
                        venue=venue,
                        year=year,
                        fieldsOfStudy="Not Available",
                        topics=topics,
                        abstract="Not Available")
        else:
            try: title=content['message']['items'][0]['title'][0];
            except: title='Not Available';

            try: authors=", ".join([author['given']+' '+author['family'] for author in content['message']['items'][0]['author']]);
            except: authors='Not Available';

            try: doi=content['message']['items'][0]['DOI'];
            except: doi='Not Available';

            try: url=self.session.get("https://doi.org/%s"%DOI, allow_redirects=True).url;
            except: url='Not Available';

            try: venue=content['message']['items'][0]['short-container-title'][0];
            except: venue='Not Available';

            try: year=content['message']['items'][0]['published-print']['date-parts'][0][0];
            except: year='Not Available';

            try: topics=content['message']['items'][0]['link'][0]['intended-application'];
            except: topics='Not Available';

            try: abstract=content['message']['items'][0]['abstract'];
            except: abstract='Not Available';

            result = dict(title=title,
                        authors=authors,
                        doi=doi,
                        url=url,
                        venue=venue,
                        year=year,
                        fieldsOfStudy="Not Available",
                        topics=topics,
                        abstract=abstract)
        return result


    def parse_doi(self, DOI):
        print("Parsing for DOI: %s"%DOI, end=" =====> ")
        try:
            response = self.session.get("https://api.semanticscholar.org/v1/paper/%s"%DOI)
            status_code, content = (response.status_code, json.loads(response.content))
            
            result = (status_code, None)

            if status_code == 200:
                result = (status_code, self.fetch_info(content, DOI))
                print("[%s:successful]"%status_code)
            else:
                print(["%s:failed"%status_code])
        except:
            print("Trying through crossref", end=" =====> ")
            try:
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
            except:
                print("[%s:failed]"%status_code)
                result = (status_code, None)
        return result