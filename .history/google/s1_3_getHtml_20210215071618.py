# This module is called from 3R Automation Component. 
import os
import sys
# pdftotree is available as part of the virtual environment for 3R Python processing
import pdftotree
import json
from pprint import pprint
import pdfminer

import ocr_extract as imgpdf

pdf_doc = json.loads(sys.argv[1])['doc_name']
html_path = json.loads(sys.argv[1])['html_path']
original_pdf_path = json.loads(sys.argv[1])['original_pdf_path']
original_html_path = json.loads(sys.argv[1])['original_html_path']
job_id = json.loads(sys.argv[1])['original_html_path']

# Use the following for testing
# pdf_doc = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/pdf/Sri_khyati_CV.pdf'
# html_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/html/Sri_khyati_CV.html'

def create_hocr(pdf_doc='', html_path='', model_path='./model/model.pkl'):
    return pdftotree.parse(pdf_doc, html_path=html_path, model_type=None, model_path=model_path, visualize=False)

create_hocr_output = None
try:
    create_hocr_output = create_hocr(pdf_doc=pdf_doc, html_path=html_path)
except pdfminer.pdfparser.PDFSyntaxError as pdfException:
    create_hocr_output = pdfException

    # Use the following for testing non PDF files
    # print(f'{os.path.basename(pdf_doc).split(".")[0]+".pdf"}')
    # print(f'{os.path.abspath(pdf_doc).split(".")[0]+".pdf"}')
    # try:
    #     # imgpdf.convert_image_to_pdf(pdf_doc, os.path(pdf_doc)+os.path.basename(pdf_doc).split('.')[0]+'.pdf')
    #     imgpdf.convert_image_to_pdf(pdf_doc, os.path.dirname(pdf_doc), os.path.abspath(pdf_doc).split(".")[0]+".pdf")
    # except Exception as exc:
    #     print(exc)

# Output of "print" statement is passed to the calling program
proc_status = "OK" if create_hocr_output == None else "Not a PDF document. Please provide a PDF file for processing."
json_out = {"pdf_doc": pdf_doc, "process_status": proc_status, "original_pdf_path":original_pdf_path, "original_html_path":original_html_path}
print(json.dumps(json_out))