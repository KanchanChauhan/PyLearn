from xhtml2pdf import pisa
from StringIO import StringIO

def create_pdf(pdf_data):
	outputFilename = "test.pdf"
	resultFile = open(outputFilename , "w+b")
    	pisa.CreatePDF(StringIO(pdf_data), dest=resultFile)
    	#return pdf