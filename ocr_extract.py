import os
import cv2
import re
import numpy as np
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pytesseract import Output
from fpdf import FPDF

################ IMAGE HANDLING METHODS #################
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

############ EXTRACT TEXT FROM IMAGE #######################
def extract_text_from_image(img, action, psm):

	#custom_config = r'-c tessedit_char_whitelist=123456789MALEPQRETHANabcdefghijklmnopqrstuvwxyz --psm 6'
	#custom_config = r'-l eng --psm 11'
	custom_config = r'-l eng --psm ' + str(psm)

	#d = pytesseract.image_to_data(img, output_type=Output.DICT)
	#print(d.keys())
	#print(d)
	img1 = None
	if (action == 1):
		img1 = remove_noise(img)
	if (action == 2):
		img1 = get_grayscale(img)
		#img1 = erode(img)
	if (action == 3):
		img1 = remove_blur(img)

	# text = pytesseract.image_to_string(img1, config=custom_config, lang='eng')
	text = 'Default'
	try:
		# text = pytesseract.image_to_string(img1, config=custom_config, lang='eng')
		text = pytesseract.image_to_string(img1)
		# pdf = pytesseract.image_to_pdf_or_hocr(Image.open(img), extension='pdf')
		# pdf = pytesseract.image_to_pdf_or_hocr(img1, config=custom_config, lang='eng')
		# with open(img.split(".")+".pdf", 'w+b') as f:
		#     f.write(pdf) # pdf type is bytes by default
	except Exception as exc:
		print(f'Exception {exc}')

	return text

############ CONVERT TEXT FILE TO PDF ##########################
def convert_text_to_pdf(text, pdf_path='./documents/pdf', filename=None):

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

	with open(textFileName, mode = 'w') as f:
	    f.write(text)

	line=1
	f = open(textFileName, "r")
	for x in f:
        	x1 = re.sub(u"(\u2014|\u2018|\u2019|\u201c|\u201d)", "", x)
        	pdf.cell(100, 10, txt = x1,ln = line, align = 'L')
        	line=line+1

	#save the pdf with name .pdf
	pdf.output(pdfFileName,'F')


############ MAIN() ####################################

#img = Image.open('Aadhaar.jpeg')

#fileName = '0001.jpg'
#fileName = '0002.jpg'
def convert_image_to_pdf(image_file, pdf_path, pdf_file):
	fileName = image_file
	head, tail = os.path.split(fileName)
	# textFileName = pdf_path
	# img = cv2.imread(fileName)
	img_cv = cv2.imread(fileName)
	img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
	# text = extract_text_from_image(img, 2, 11)
	text = extract_text_from_image(img_rgb, 2, 3)
	print(f'Extracted {text}')
	# print(text)
	convert_text_to_pdf(text, pdf_path, tail.split(".")[0]+".pdf")

# fileName = 'PAN.jpeg'
# textFileName = os.path.basename(fileName).split('.')[0]
# img = cv2.imread(fileName)
# text = extract_text_from_image(img,2,6)
# print(text)
# convert_text_to_pdf(text,textFileName)
