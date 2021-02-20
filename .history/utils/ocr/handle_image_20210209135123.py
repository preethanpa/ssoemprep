import os
import cv2
import re
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output
from fpdf import FPDF

'''
IMAGE HANDLING METHODS
'''
# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# blur removal
def remove_blur(image):
    return cv2.medianBlur(image,5)

# noise removal
def remove_noise(image):
	return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)

#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#dilation
def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)

#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

def extract_pdf_from_image(fileName='', pdf_path='', action='', psm=3):
	'''
	Extract text from image and save as PDF.
	fileName=''
	pdf_path='', 
	action='',
	psm=3
	'''

	#custom_config = r'-c tessedit_char_whitelist=123456789MALEPQRETHANabcdefghijklmnopqrstuvwxyz --psm 6'
	#custom_config = r'-l eng --psm 11'
	custom_config = r'-l eng --psm ' + str(psm)

	pdfdir = pdf_path
	if not os.path.exists(pdfdir):
    		os.makedirs(pdfdir)

	pdfFileName = os.path.basename(fileName).split('.')[0] + '.pdf'
	pdfFilePath = pdfdir + '/' + pdfFileName
	print(f'PDF File Path {pdfFilePath}')

	#d = pytesseract.image_to_data(img, output_type=Output.DICT)
	img = cv2.imread(fileName)

	if (action == 1):
		img1 = remove_noise(img)
	if (action == 2):
		img1 = get_grayscale(img)
		#img1 = erode(img)
	if (action == 3):
		img1 = remove_blur(img)


	#text = pytesseract.image_to_string(img1, config=custom_config,lang='eng')
	text = pytesseract.image_to_pdf_or_hocr(img1, extension='pdf')

	with open(pdfFilePath, mode = 'w+b') as f:
	    f.write(text)
	return pdf

def convert_text_to_pdf(text='', pdf_path='', filename=''):
	'''
	Convert text file to PDF
	'''
	tempdir = "/tmp"
	pdfdir = pdf_path

	textFileName = tempdir + '/' + filename + ".txt"
	pdfFileName = pdfdir + '/' + filename + ".pdf"

	if not os.path.exists(tempdir):
    		os.makedirs(tempdir)
	if not os.path.exists(pdfdir):
    		os.makedirs(pdfdir)

	# save FPDF() class into a
	# variable pdf
	pdf = FPDF()

	# Add a page
	pdf.add_page()

	# set style and size of font
	# that you want in the pdf
	pdf.set_font("Arial", size = 15)

	with open(textFileName, mode = 'w+b') as f:
	    f.write(text)

	line = 1
	f = open(textFileName, "r")
	for x in f:
        	x1 = re.sub(u"(\u2014|\u2018|\u2019|\u201c|\u201d)", "", x)
        	pdf.cell(100, 10, txt=x1, ln=line, align='L')
        	line=line+1

	#save the pdf with name .pdf
	pdf.output(pdfFileName,'F')