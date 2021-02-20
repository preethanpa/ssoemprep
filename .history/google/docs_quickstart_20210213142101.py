from __future__ import print_function
import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.activity', 'https://www.googleapis.com/auth/drive.metadata', 'https://www.googleapis.com/auth/drive']# 'https://www.googleapis.com/auth/documents.readonly']

# The ID of a sample document.
# DOCUMENT_ID = '1bQkFcQrWFHGlte8oTVtq_zyKGIgpFlWAS5_5fi8OzjY'
DOCUMENT_ID = '1t59BmxA038_El4kwyxQruqOJv_AvkWY3'

def main():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """

    from google.oauth2 import service_account
    import googleapiclient.discovery

    SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/sqlservice.admin', 'https://www.googleapis.com/auth/drive.file']

    SERVICE_ACCOUNT_FILE = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/google/domain-wide-credentials-gdrive.json'

    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject('abhi@third-ray.com')
    drive_credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject='abhi@third-ray.com')
            # SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # service = build('docs', 'v1', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=drive_credentials)
    # sqladmin = googleapicliexnt.discovery.build('sqladmin', 'v1beta3', credentials=drive_credentials)

    # Retrieve the documents contents from the Docs service.
    # document = service.documents().get(documentId=DOCUMENT_ID).execute()
    
    # print('The title of the document is: {}'.format(document.get('title')))

    # sqladmin = googleapiclient.discovery.build('sqladmin', 'v1beta3', credentials=drive_credentials)
    # response = sqladmin.instances().list(project='domain-wide-gdrive').execute()
    # print(response)
    request = drive_service.files().get_media(fileId=DOCUMENT_ID)
    print(request)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False

    while done is False:
        status, done = downloader.next_chunk()
    #     print(f"Download % {int(status.progress() * 100)}")

if __name__ == '__main__':
    main()