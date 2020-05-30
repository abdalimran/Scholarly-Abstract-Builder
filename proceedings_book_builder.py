from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import PageBreak
from reportlab.lib.units import inch

class ProceedingsBookBuilder:
    
    def __init__(self, file_name, proceedings_title='Abdullah Al Imran'):
        self.proceedings = SimpleDocTemplate("%s.pdf"%file_name, pagesize=letter, 
                                             rightMargin=72, leftMargin=72, 
                                             topMargin=72, bottomMargin=18)
        self.width, self.height = letter
        self.proceedings.title = proceedings_title
        self.style = getSampleStyleSheet()
        self.style['Heading1'].alignment=1
        self.style['Heading4'].alignment=1
        self.style['BodyText'].fontName='Times-Roman'
        self.style['BodyText'].fontSize=12
        self.justify_style=self.style['BodyText']
        self.justify_style.alignment=TA_JUSTIFY
        self.cover_style=self.style['Heading2']
        self.cover_style.alignment=1
        
        self.flowables = list()
        
    def cover_pdf(self, proceedings_info):
        self.flowables.append(Paragraph(proceedings_info['title'], self.style['Heading1']))
        self.flowables.append(Spacer(1, 20))
        self.flowables.append(Paragraph(proceedings_info['authors'], self.cover_style))
        self.flowables.append(Spacer(1, 100))
        self.flowables.append(Paragraph("<b>Publisher: </b>%s"%proceedings_info['publisher'], self.cover_style))
        self.flowables.append(Paragraph("<b>Publication Date: </b>%s"%proceedings_info['datePublished'], self.cover_style))
        self.flowables.append(Paragraph("<b>ISBN: </b>%s"%proceedings_info['isbn'], self.cover_style))
        self.flowables.append(PageBreak())

    def paper_pdf(self, track, paper):
        self.flowables.append(Paragraph(paper['title'], self.style['Heading1']))
        self.flowables.append(Paragraph(paper['authors'], self.style['Heading4']))
        self.flowables.append(Spacer(1, 12))

        self.flowables.append(Paragraph("Information", self.style['Heading2']))
        self.flowables.append(Paragraph("<b>Track: </b>%s"%track, self.style['BodyText'], bulletText='-'))
        self.flowables.append(Paragraph("<b>DOI: </b>%s"%paper['doi'], self.style['BodyText'], bulletText='-'))
        self.flowables.append(Paragraph("<b>URL: </b><link href='%s'>%s</link>"%(paper['url'],paper['url']), self.style['BodyText'], bulletText='-'))
        self.flowables.append(Paragraph("<b>Venue: </b>%s"%paper['venue'], self.style['BodyText'], bulletText='-'))
        self.flowables.append(Paragraph("<b>Year: </b>%s"%paper['year'], self.style['BodyText'], bulletText='-'))
        self.flowables.append(Paragraph("<b>Fields of Study: </b>%s"%paper['fieldsOfStudy'], self.style['BodyText'], bulletText='-'))
        self.flowables.append(Paragraph("<b>Topics: </b>%s"%paper['topics'], self.justify_style, bulletText='-'))

        self.flowables.append(Spacer(1, 12))
        self.flowables.append(Paragraph("Abstract", self.style['Heading2']))
        self.flowables.append(Paragraph(paper['abstract'], self.style['BodyText']))
        self.flowables.append(PageBreak())
        
    def addPageNumber(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        page_num = canvas.getPageNumber()
        text = "%s"%page_num
        canvas.drawCentredString(4.25*inch, 0.50*inch, text)
        
    def build_pdf_book(self, proceedings_data):
        for track in proceedings_data.keys():
            if track == "proceedings_info":
                self.cover_pdf(proceedings_data[track][0])
            else:
                for paper in proceedings_data[track]:
                    self.paper_pdf(track, paper)
                    
        self.proceedings.build(self.flowables, 
                               onFirstPage=self.addPageNumber, 
                               onLaterPages=self.addPageNumber)
        
        print("Proceedings book has been created!")