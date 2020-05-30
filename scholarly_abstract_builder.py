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
                
    def build(self, dump_data=False, dump_filename=None):
        proceedings = DBLPParser()
        proceedings_data = proceedings.parse_proceedings(self.DBLP_LINK, self.no_track)
        
        if dump_data==True and dump_filename!=None:
            self.dump_data(proceedings_data, dump_filename+"_DBLP_data")
            print("Proceedings metadata has been dumped from DBLP!")            
        else:
            print("'dump_filename' is missing!")
        
        papers = PaperParser()
        proceedings_book = {}
        
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
            
        if dump_data==True and dump_filename!=None:
            self.dump_data(proceedings_book, dump_filename+"_book_data")
            print("Proceedings book data has been dumped!")
            
        book_builder = ProceedingsBookBuilder(file_name=self.TITLE)
        book_builder.build_pdf_book(proceedings_book)

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--link", "-l", help="set dblp link")
    parser.add_argument("--title", "-t", help="set book title")
    parser.add_argument("--notrack", "-nt", help="set track", type=eval, choices=[True, False], default='False')
    parser.add_argument("--dump", "-d", help="set dump data", type=eval, choices=[True, False], default='True')
    args = parser.parse_args()

    DBLP_LINK = args.link
    TITLE = args.title
    no_track = args.notrack

    builder = ScholarlyAbstractBuilder(DBLP_LINK=DBLP_LINK,
                                       TITLE=TITLE,
                                       no_track=no_track)

    builder.build(dump_data=args.dump, dump_filename=TITLE)