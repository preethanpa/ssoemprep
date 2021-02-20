# This module is called from 3R Automation Component. 
import os
import sys
# pdftotree is available as part of the virtual environment for 3R Python processing
import pdftotree
import json
from pprint import pprint
import pdfminer
import matplotlib.pyplot as plt

import ocr_extract as imgpdf

from utils.ocr.handle_image import *

# pdf_doc = json.loads(sys.argv[1])['doc_name']
pdf_doc = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/images/PAN_Card_Scan_AKC.png'
# html_path = json.loads(sys.argv[1])['html_path']
html_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/html/'+os.path.basename(pdf_doc).split('.')[0] + '.html'
print(f'HTML Path is set to {html_path}')
path_if_not_pdf_doc = ''

pdf_doc_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/pdf'

# Use the following for testing
# pdf_doc = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/pdf/Sri_khyati_CV.pdf'
# html_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/html/Sri_khyati_CV.html'

def create_hocr(pdf_doc='', html_path='', model_path='./model/model.pkl'):
    return pdftotree.parse(pdf_doc, html_path=html_path, model_type=None, model_path=model_path, visualize=False)

create_hocr_output = None
try:
    create_hocr_output = create_hocr(pdf_doc=pdf_doc, html_path=html_path)
except pdfminer.pdfparser.PDFSyntaxError as pdfException:
    print(f'Exception 1 {pdfException}')
    create_hocr_output = pdfException
    path_if_not_pdf_doc = pdf_doc

    try:
        mark_region(path_if_not_pdf_doc)
        # pdf_doc = extract_pdf_from_image(pdf_doc, pdf_path=pdf_doc_path, action=1, psm=11)
        # (image, line_items_coordinates) = mark_region(path_if_not_pdf_doc)
        # print(f'Computed {image} and {line_items_coordinates}')
        # # load the original image
        # # image = cv2.imdecode(image, cv2.IMREAD_ANYCOLOR)
        # image = cv2.imread(path_if_not_pdf_doc, cv2.COLOR_BGR2GRAY)
        # # try:
        # # get co-ordinates to crop the image
        # # c = line_items_coordinates[1]
        # c = line_items_coordinates[0]
        # print(f'line_items_coordnates {c}')
        # # cropping image img = image[y0:y1, x0:x1]
        # img = image[c[0][1]:c[1][1], c[0][0]:c[1][0]]    
        # print(f'img is {img}')
        # plt.figure(figsize=(10,10))
        # plt.imshow(img)
        # # convert the image to black and white for better OCR
        # ret,thresh1 = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
        # # pytesseract image to string to get results
        # text = str(pytesseract.image_to_string(thresh1, config='--psm 6'))
        # print(f'text is {text}')
        # convert_text_to_pdf(text, pdf_doc_path, os.path.basename(pdf_doc).split('.')[0])
        # create_hocr_output = create_hocr(pdf_doc=pdf_doc, html_path=html_path)
        # # except Exception as exc1_1:
        # #     print(f'Exception 1.1.1 {exc1_1}')
        pass
    except Exception as exc1:
        print(f'Exception 1.1 {exc1}')
    except Exception as exc:
        create_hocr_output = Exception
        print(f'Exception 2 {exc}')
    # extract_pdf_from_image(pdf_doc, pdf_path=pdf_doc_path, action=2, psm=6)


    # Use the following for testing non PDF files
    # print(f'{os.path.basename(pdf_doc).split(".")[0]+".pdf"}')
    # print(f'{os.path.abspath(pdf_doc).split(".")[0]+".pdf"}')
    # try:
    #     # imgpdf.convert_image_to_pdf(pdf_doc, os.path(pdf_doc)+os.path.basename(pdf_doc).split('.')[0]+'.pdf')
    #     imgpdf.convert_image_to_pdf(pdf_doc, os.path.dirname(pdf_doc), os.path.abspath(pdf_doc).split(".")[0]+".pdf")
    # except Exception as exc:
    #     print(exc)

# Output of "print" statement is passed to the calling program
proc_status = "OK" if create_hocr_output == None else "Not a PDF document or unable to process image at path "+path_if_not_pdf_doc
json_out = {"pdf_doc": pdf_doc, "process_status": proc_status}
json_out = {"message": "We are testing/making some changes to this API, please try after in about 30 mins. Sorry for the inconvenience."}
print(json_out)