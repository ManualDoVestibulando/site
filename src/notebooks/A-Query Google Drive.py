# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: 'Python 3.10.4 (''venv'': venv)'
#     language: python
#     name: python3
# ---

# %%
import pandas as pd

# %%
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# %% [markdown]
# ## Support functions

# %%
def run_on_drive_api(func):
    def wrapper(*args, **kwargs):
        try:
            service = build('drive', 'v3',
                            developerKey='AIzaSyBU7WIsMv5LvRD3xt8ZnV5fqfMY40iEHS8')
            return func(*args, service=service, **kwargs)
        except HttpError as error:
            print(f'An error occurred:\n\n{error}')
    return wrapper


# %%
def is_essay_file(drive_item):
    return any(x in drive_item['mimeType'] for x in ['image', 'pdf'])


# %%
@run_on_drive_api
def recreate_file_tree(initial_folder_id, service=None):
    query = f"'{initial_folder_id}' in parents"
    results = service.files().list(q=query).execute()
    items = results.get('files')
    file_items = {}

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            file_items[item['name']] = recreate_file_tree(item['id'])
        else:
            file_items[item['name']] = item

    return file_items


# %%
file_items = recreate_file_tree('1NxxkhOfH4eB0v6E0leGtG5hHo2amYKmG')
file_items

# %%
print(file_items.keys())

# %%
enem_tree = file_items['Enem']
fuvest_tree = file_items['Fuvest']

ENEM_COLS = [
    'ano',
    'nota',
    'c1',
    'c2',
    'c3',
    'c4',
    'c5',
    'drive_id',
    'url',
]

FUVEST_COLS = [
    'ano',
    'nota',
    'drive_id',
    'url',
]

# %%
DRIVE_VIEW_BASE_URL = 'https://drive.google.com/file/d/{}/view'


# %%
def parse_enem_essays(filetree, base_view_url, columns):
    data = []
    for raw_year, file_dict in filetree.items():
        year = raw_year.split('.')[0]
        essay_dict = {filename: item for filename, item in file_dict.items() if is_essay_file(item)}
        for filename, drive_item in essay_dict.items():
            marks = filename.split('_')[0].split('-')
            if len(marks) > 1:
                final_marks = marks
            else:
                final_marks = [marks[0], None, None, None, None, None]
            file_view_url = base_view_url.format(drive_item['id'])
            data.append([year, *final_marks, drive_item['id'], file_view_url])
    
    return pd.DataFrame(data=data, columns=columns).convert_dtypes()


# %%
enem_parsed = parse_enem_essays(enem_tree, DRIVE_VIEW_BASE_URL, ENEM_COLS)
enem_parsed


# %%
def parse_fuvest_essays(filetree, base_view_url, columns):
    data = []
    for year, file_dict in filetree.items():
        if year != '50.pdf': # One file was misplaced
            essay_dict = {filename: item for filename, item in file_dict.items() if is_essay_file(item)}
            for filename, drive_item in essay_dict.items():
                mark = filename.split('_')[0].split('-')[0].replace(',', '.')
                file_view_url = base_view_url.format(drive_item['id'])
                data.append([year, mark, drive_item['id'], file_view_url])
    
    return pd.DataFrame(data=data, columns=columns).convert_dtypes()


# %%
fuvest_parsed = parse_fuvest_essays(fuvest_tree, DRIVE_VIEW_BASE_URL, FUVEST_COLS)
fuvest_parsed

# %%
enem_parsed.to_csv('../../data/4_final/redacoes/enem/2020.csv', index=None)
fuvest_parsed.to_csv('../../data/4_final/redacoes/fuvest/2020.csv', index=None)


# %% [markdown]
# ## Experimentation

# %%
def drive_api_key():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    try:
        service = build('drive', 'v3',
                        developerKey='AIzaSyBU7WIsMv5LvRD3xt8ZnV5fqfMY40iEHS8')

        # Call the Drive v3 API
        folder_id = '1NxxkhOfH4eB0v6E0leGtG5hHo2amYKmG'
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query).execute()
        items = results.get('files')

        if not items:
            print('No files found.')
            return
        print('Files:')
        print(type(items))
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            print(item['mimeType'])
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                new_result = service.files().list(q=f"'{item['id']}' in parents").execute()
                new_items = new_result.get('files')
                for new_item in new_items:
                    print(u'{0} ({1})'.format(new_item['name'], new_item['id']))
                    print(new_item['mimeType'])

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred:\n\n{error}')


# %%
drive_api_key()


# %%
def drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'service.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    try:
        service = build('drive', 'v3', credentials=credentials)

        # Call the Drive v3 API

        # file_path = '/home/tomaz/Downloads/Apostila---Produtividade-Na-Pratica-Online.pdf'
        # file_metadata = {'name': 'pdf_exemplo.pdf'}
        # media = MediaFileUpload(file_path, mimetype='application/pdf')
        # file = service.files().create(body=file_metadata,
        #                                     media_body=media,
        #                                     fields='id').execute()
        #
        # result = service.about().get(fields='storageQuota').execute()
        # print(result)

        # results = service.files().list(
        #     pageSize=10).execute()
        # items = results.get('files', [])
        #
        # if not items:
        #     print('No files found.')
        #     return
        # print('Files:')
        # for item in items:
        #     print(u'{0} ({1})'.format(item['name'], item['id']))

        # file_id = '1-H2egFbxXfJPM2EifumTIJMwQH9Q5DNU'
        # permissions = {
        #     'type': 'anyone',
        #     'role': 'reader',
        # }
        # service.permissions().create(
        #     fileId=file_id,
        #     body=permissions,
        #     fields='id',
        # ).execute()

        from googleapiclient.http import MediaIoBaseDownload

        file_id = '1-H2egFbxXfJPM2EifumTIJMwQH9Q5DNU'
        request = service.files().get_media(fileId=file_id)
        with open('example.pdf', 'wb') as output:
            downloader = MediaIoBaseDownload(output, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}")

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


# %%
drive_service()

# %%
