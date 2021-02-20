from __future__ import print_function
import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import  MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import googleapiclient.discovery

import gdoc_down as gdownload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.activity', 'https://www.googleapis.com/auth/drive.metadata', 'https://www.googleapis.com/auth/drive']# 'https://www.googleapis.com/auth/documents.readonly']

# The ID of a sample document.
# DOCUMENT_ID = '1bQkFcQrWFHGlte8oTVtq_zyKGIgpFlWAS5_5fi8OzjY'
DOCUMENT_ID = '1sXQie19gQBRHODebxBZv4xUCJy-9rGpnlpM7_SUFor4'
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/sqlservice.admin', 'https://www.googleapis.com/auth/drive.file']

# SERVICE_ACCOUNT_FILE = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/google/domain-wide-credentials-gdrive.json'
SERVICE_ACCOUNT_FILE = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/google/app-automation-service-account-thirdrayai-1612747564720-415d6ebd6001.json'


def get_document():
    """Use Google Docs API to find a document file.
    Download the file as a PDF file.
    """

    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES) 
            #, subject='abhi@third-ray.com')
    docs_service = build('docs', 'v1', credentials=credentials)#.with_subject('abhi@third-ray.com'))
    print(dir(docs_service.documents()))

    document = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
    
    return document

def download_document(document_resource):
    print(document_resource)
    # gdownload.core.GDocDown(service=document_resource)

download_document(get_document())