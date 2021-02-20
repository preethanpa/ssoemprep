import os
import cv2
import re
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output
from fpdf import FPDF

from utils.ocr.handle_image import *

############ MAIN() ####################################

#img = Image.open('Aadhaar.jpeg')

#fileName = '0001.jpg'
#fileName = '0002.jpg'
fileName = 'Aadhaar.jpeg'
#head, tail = os.path.split(fileName)
#textFileName = os.path.basename(fileName).split('.')[0]

extract_pdf_from_image(fileName,1,11)
#convert_text_to_pdf(text,textFileName)

fileName = 'PAN.jpeg'
#textFileName = os.path.basename(fileName).split('.')[0]
extract_pdf_from_image(fileName,2,6)
#convert_text_to_pdf(text,textFileName)
