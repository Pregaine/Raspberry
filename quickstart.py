# from pydrive.auth import GoogleAuth

# gauth = GoogleAuth()
# auth_url = gauth.GetAuthUrl() # Create authentication url user needs to visit
# code = AskUserToVisitLinkAndGiveCode(auth_url) # Your customized authentication flow
# gauth.Auth(code) # Authorize and build service from the code


# from pydrive.auth import GoogleAuth

# gauth = GoogleAuth()
# Create local webserver and auto handles authentication.
# gauth.LocalWebserverAuth()

# from pydrive.drive import GoogleDrive

# drive = GoogleDrive(gauth)

# file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
# file1.SetContentString('Hello World!') # Set content of the file from given string.
# file1.Upload()

# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive

# gauth = GoogleAuth()
# gauth.CommandLineAuth() #透過授權碼認證
# drive = GoogleDrive(gauth)

# file1 = drive.CreateFile({'title': 'Hello.txt'})  # 建立檔案
# file1.SetContentString('Hello World!') # 編輯檔案內容
# file1.Upload() #檔案上傳

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'

SCOPES = 'https://www.googleapis.com/auth/drive.activity'

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            
    file_metadata = {'name': '1101_台泥_20190614.csv'}
    
    media = MediaFileUpload( '全台卷商交易資料_20190614/1101_台泥_20190614.csv', mimetype = 'text/csv' )
                        
    file = service.files().create( body=file_metadata, media_body=media, fields='id' ).execute()
    print( 'File ID: %s'.format( file.get('id') ) )

if __name__ == '__main__':
    main()