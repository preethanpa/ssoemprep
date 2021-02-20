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
import json

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

doc_types = {
    "application/vnd.google-apps.document": "gdoc",
    # "application/vnd.google-apps.folder": "folder",
    "application/vnd.google-apps.spreadsheet": "gsheet",
    "application/vnd.google-apps.presentation": "gslide"
}

drive_files_list = [] if (sys.argv is None or sys.argv[1] is None) else json.loads(sys.argv[1])

# google_file_type = 'gdoc' if (sys.argv is None or sys.argv[1] is None or sys.argv[1].google_file_type is None) else sys.argv[1].google_file_type
# target_file_type = 'pdf' if (sys.argv is None or sys.argv[1] is None or sys.argv[1].target_file_type is None) else sys.argv[1].target_file_type
# location = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/drive_documents/'+drive_files_list.get('job_id')+'/pdf/' 
# document_id = None if (sys.argv[1] is None or sys.argv[1].file_location is None) else sys.argv[1].document_id
document_id = ''

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

def download_drive_file(resource=None, document_id=None, google_file_type='gdoc', target_type=None, target_location=None):
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
        try:
            content = resource.files().export(fileId=document_id, mimeType=mimeType).execute()
            try:
                with open(target_location+google_file_type+'-'+document_id+extension, "wb") as file:
                    file.write(content)
                return {"status": "OK", "message": google_file_type+'-'+document_id+extension+" has been added to data lake."}
            except Exception as exc_in:
                return {"document_id": document_id"status": "Exception", "message": exc_in}
        except Exception as exc_out:
            return {"document_id": document_id, "status": "Exception", "message": exc_out}


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
        elif google_file_ext == 'gslide':
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

if drive_files_list == []:
    print(json.dumps(drive_files_list))
else:
    location = os.path.join('/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/drive_documents/', drive_files_list.get('job_id')+'/pdf/')
    os.makedirs(location) 
    response_message = {
        "status": "OK",
        "processed_files": []
    }
    for index, item in enumerate(drive_files_list.get('files')):
        try:
            google_file_type = doc_types[item.get('mimeType')]
            drive_document_id = item.get('id')
            target_file_type = "pdf"
            dl_response = download_drive_file(resource=get_resource(domain_wide_delegate=False), document_id=drive_document_id, google_file_type=google_file_type, target_type=target_file_type, target_location=location)
            response_message["processed_files"].append(dl_response)
        except KeyError as ke:
            pass
    print(json.dumps(response_message))

# print(download_drive_file(resource=get_resource(domain_wide_delegate=False)), google_file_type=google_file_type, target_type=target_file_type, target_location=location)