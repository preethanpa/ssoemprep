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
import inspect
import sys

SCOPES = ['https://www.googleapis.com/auth/documents', 
    'https://www.googleapis.com/auth/documents.readonly', 
    'https://www.googleapis.com/auth/documents.readonly', 
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]

# The ID of a sample document.
# DOCUMENT_ID = '1bQkFcQrWFHGlte8oTVtq_zyKGIgpFlWAS5_5fi8OzjY'
DOCUMENT_ID = '1sXQie19gQBRHODebxBZv4xUCJy-9rGpnlpM7_SUFor4'
# SERVICE_ACCOUNT_FILE = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/google/domain-wide-credentials-gdrive.json'
SERVICE_ACCOUNT_FILE = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/google/app-automation-service-account-thirdrayai-1612747564720-415d6ebd6001.json'
UPLOAD_FILE_LOCATION = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/pdf/'

google_file_type = 'gdoc' if (sys.argv is None or sys.argv[1] is None or sys.argv[1].google_file_type is None) else sys.argv[1].google_file_type

google_file_type = 'gdoc' if (sys.argv is None or sys.argv[1] is None or sys.argv[1].google_file_type is None) else sys.argv[1].google_file_type
target_file_type = 'pdf' if (sys.argv is None or sys.argv[1] is None or sys.argv[1].target_file_type is None) else sys.argv[1].target_file_type
location = '' if (sys.argv is None or sys.argv[1] is None or sys.argv[1].file_location is None) else sys.argv[1].file_location
document_id = None if (sys.argv[1] is None or sys.argv[1].file_location is None) else sys.argv[1].document_id


def get_resource(domain_wide_delegate=False, user_to_impersonate=None):
    """Prepare a Google Drive resource object based on credentials.
    """
    credentials = None
    # use subject in case of domain-wide delegation
    if domain_wide_delegate:
        if user_to_impersonate is not None:
            credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=user_to_impersonate) 
    else:
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES) 

    if credentials is None:
        return credentials
    else:
        drive_service = build('drive', 'v3', credentials=credentials)
        return drive_service

def download_drive_file(resource=None, google_file_type='gdoc', target_type=None, location=None):
    """Downloads a Google Drive file using the provided resource.
    If google_file_type is passed as None, then 'gdoc' / Google Doc is default.
    If target_type is passed as None, then 'application/pdf' is default.
    If location is none, then use environment variable UPLOAD_FILE_LOCATION as default
    """
    # print(dir(resource.files())) #Get resource methods with dir.
    if resource is None:
        raise Exception('Invalid credentials. Provide subject email addredd for Drive-wide delegation')
    else:
        extension, mimeType = extension_mime_type(google_file_type, target_type)
        content = resource.files().export(fileId=DOCUMENT_ID, mimeType=mimeType).execute()
        if location is None:
            location = UPLOAD_FILE_LOCATION
        with open(location+type+'-'+DOCUMENT_ID+extension, "wb") as file:
            file.write(content)
    return {"status": "OK", "message": type+'-'+DOCUMENT_ID+extension+" has been added to data lake."}

def extension_mime_type(google_file_ext=None, format=None):
    export_type = None
    if google_file_ext is not None:
        if google_file_ext == 'gdoc':
            if format == 'docx':
                export_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif format == 'epub':
                export_type = 'application/epub+zip'
            elif format == 'html':
                export_type = 'text/html'
            elif format == 'odt':
                export_type = 'application/vnd.oasis.opendocument.text'
            elif format == 'pdf':
                export_type = 'application/pdf'
            elif format == 'rtf':
                export_type = 'application/rtf'
            elif format == 'tex':
                export_type = 'application/zip'
            elif format == 'txt':
                export_type = 'text/plain'
            elif format == 'html.zip':
                export_type = 'application/zip'
            else:
                raise Exception('Unknown format "{}"'.format(format))
        elif google_file_ext == 'gsheet':
            if format == 'csv':
                export_type = 'text/csv'
            elif format == 'html.zip':
                export_type = 'application/zip'
            elif format == 'ods':
                export_type = 'application/x-vnd.oasis.opendocument.spreadsheet'
            elif format == 'pdf':
                export_type = 'application/pdf'
            elif format == 'tsv':
                export_type = 'text/tab-separated-values'
            elif format == 'xlsx':
                export_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                raise Exception('Unknown format "{}"'.format(format))
        elif google_file_ext == 'gslides':
            if format == 'odp':
                export_type = 'application/vnd.oasis.opendocument.presentation'
            elif format == 'pdf':
                export_type = 'application/pdf'
            elif format == 'pptx':
                export_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            elif format == 'txt':
                export_type = 'text/plain'
            else:
                raise Exception('Unknown format "{}"'.format(format))
        else:
            raise Exception('Unknown Google document extension "{}"'.format(google_file_ext))
        
    return '.'+format, export_type

print(download_drive_file(resource=get_resource(domain_wide_delegate=False)), google_file_type=google_file_type, target_type=target_file_type, location=location)