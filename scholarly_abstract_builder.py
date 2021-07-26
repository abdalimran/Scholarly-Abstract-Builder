from dblp_parser import DBLPParser
from paper_parser import PaperParser
from proceedings_book_builder import ProceedingsBookBuilder
import pickle
import time
import argparse

class ScholarlyAbstractBuilder:
    
    def __init__(self, DBLP_LINK, TITLE, no_track=False):
        self.DBLP_LINK=DBLP_LINK
        self.TITLE=TITLE
        self.no_track=no_track
    
    def dump_data(self, data, file_name):
        with open("%s.dump"%file_name,'wb') as file:
            pickle.dump(data, file)
                
    def build(self, dump_data=False, dump_filename=None, makebook=False, makedata=False):
        proceedings = DBLPParser()

        if self.DBLP_LINK.find("search?q=") != -1:
            proceedings_data = proceedings.parse_for_query(self.DBLP_LINK)
            self.TITLE = self.DBLP_LINK.partition("search?q=")[2].replace("%20"," ")
        else:
            proceedings_data = proceedings.parse_proceedings(self.DBLP_LINK, self.no_track)
        
        if dump_data==True and dump_filename!=None and proceedings_data['research']:
            self.dump_data(proceedings_data, dump_filename+"_DBLP_data")
            print("Proceedings metadata has been dumped from DBLP!")            
        elif dump_data==True and dump_filename==None:
            print("'dump_filename' is missing!")
        else:
            pass
        
        papers = PaperParser()
        proceedings_book = {}
        
        if proceedings_data['research']:
            for no, track in enumerate(proceedings_data):
                if no==0:
                    proceedings_book[track] = [proceedings_data[track]]
                else:
                    proceedings_book[track] = []
                    for doi in proceedings_data[track]:
                        status_code, paper = papers.parse_doi(doi)
                        if status_code==200:
                            proceedings_book[track].append(paper)
                print('{}. "{}" track DONE!\n'.format(no, track))

            if makebook==True and makedata==True:
                book_builder = ProceedingsBookBuilder(file_name=self.TITLE)        
                book_builder.build_pdf_book(proceedings_book)
                dataset = book_builder.build_dataset(proceedings_book)
                dataset.to_csv("%s.csv"%self.TITLE, index=False)
            elif makebook==False and makedata==True:
                book_builder = ProceedingsBookBuilder(file_name=self.TITLE)
                dataset = book_builder.build_dataset(proceedings_book)
                dataset.to_csv("%s.csv"%self.TITLE, index=False)
            else:
                book_builder = ProceedingsBookBuilder(file_name=self.TITLE)        
                book_builder.build_pdf_book(proceedings_book)                
        else:
            print("No papers found!")
            
        if dump_data==True and dump_filename!=None and proceedings_data['research']:
            self.dump_data(proceedings_book, dump_filename+"_book_data")
            print("Proceedings book data has been dumped!")

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--link", "-l", help="set dblp link")
    parser.add_argument("--title", "-t", help="set book title")
    parser.add_argument("--notrack", "-nt", help="set track", type=eval, choices=[True, False], default='False')
    parser.add_argument("--dump", "-d", help="set dump data", type=eval, choices=[True, False], default='True')
    parser.add_argument("--makebook", "-mb", help="set make book", type=eval, choices=[True, False], default='True')
    parser.add_argument("--makedata", "-md", help="set make data", type=eval, choices=[True, False], default='False')
    args = parser.parse_args()

    DBLP_LINK = args.link
    TITLE = args.title
    no_track = args.notrack
    makebook = args.makebook
    makedata = args.makedata

    builder = ScholarlyAbstractBuilder(DBLP_LINK=DBLP_LINK,
                                       TITLE=TITLE,
                                       no_track=no_track)

    builder.build(dump_data=args.dump, dump_filename=TITLE, makebook=makebook, makedata=makedata)