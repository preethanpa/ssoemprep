import zipfile
import os
import logging
import glob

def prepare_html(pdf_file='', html_path='', zip_file=''):
    html_list = []
    zip_path = os.path.dirname(zip_file)
    #logging.info(f'Zipfile is {zip_file}')
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            #logging.info(f'===> zipref is {zip_ref}')
            zip_ref.extractall(zip_path)
            # os.remove(zip_file)
    except FileNotFoundError:
        #logging.info(f'Error opening zip file error={FileNotFoundError}')
        pass
    html_list = [f for f in sorted(glob.glob(zip_path+"/*.html"))]
    logging.info(f'===> HTML Files list={html_list}')
    try:
        with open(html_path+os.path.splitext(pdf_file)[0]+'.html', "wb") as outfile:
            #logging.info(f'===> outfile is {outfile}')
            #logging.info(f'===> html_path is {html_path}')
            for f in html_list:
                with open(f, "rb") as infile:
                    outfile.write(infile.read())
    except FileNotFoundError:
        #logging.info(f'Error opening outfile {html_path+os.path.splitext(pdf_file)[0]+".html"} error={FileNotFoundError}')
        pass