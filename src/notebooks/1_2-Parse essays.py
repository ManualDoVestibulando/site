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
#     display_name: 'Python 3.10.1 64-bit (''mdv'': conda)'
#     language: python
#     name: python3
# ---

# %%
from time import time_ns
import tempfile
import os

from PIL import Image
import pandas as pd
import numpy as np
import glob

# %%
ESSAYS_DIR = '../../data/1_initial/redacoes/enem/2021'
FORM_PATH = '../../data/1_initial/forms/2021.csv'
FORM_EXAM_TYPE = 'Enem'
IMAGE_TYPES = ('*.png', '*.jpg', '*.jpeg', '*.tif', '*.tiff')
MANUAL_REVISION_DIR = '../../data/2_intermediate/redacoes/enem/2021'
OUTPUT_PATH = '../../data/3_processed/redacoes/enem/2021.csv'

# %%
images = []
for type_ in IMAGE_TYPES:
    image_path = os.path.join(ESSAYS_DIR, type_)
    images.extend(glob.glob(image_path))
images.sort(key=os.path.getmtime)
print(len(images))
print(images)

# %%
form = pd.read_csv(FORM_PATH).convert_dtypes()
exam_mask = form['Forma de ingresso'].str.contains(FORM_EXAM_TYPE)
essay_mask = np.logical_not(form['Envie aqui o espelho da sua redação.1'].isna())
exam_essays = form.loc[np.logical_and(exam_mask, essay_mask)]
exam_essays


# %%
def parse_enem_essays(row):
    return pd.Series({
        'ano':  row['Qual o seu ano de ingresso?'],
        'nota': row['Redação'],
        'c1':   row['Nota na Competência 1'],
        'c2':   row['Nota na Competência 2'],
        'c3':   row['Nota na Competência 3'],
        'c4':   row['Nota na Competência 4'],
        'c5':   row['Nota na Competência 5'],
    })

enem_essays_processed = exam_essays.apply(parse_enem_essays,
                                          axis=1)
enem_essays_processed


# %%
def parse_fuvest_essays(row):
    return pd.Series({
        'ano':  row['Qual o seu ano de ingresso?'],
        'nota': row['Nota da redação'],
    })

fuvest_essays_processed = exam_essays.apply(parse_fuvest_essays,
                                            axis=1)
fuvest_essays_processed

# %%
expected_ratio = 0.74
threshold = 0.025
normalised_crop_height = 0.1977
exam_essays_processed = enem_essays_processed

manual_revision_tmp = tempfile.mkdtemp(prefix='manual_revision_')
no_manual_revision_tmp = tempfile.mkdtemp(prefix='no_manual_revision_')

for i, image_path in enumerate(images):
    with Image.open(image_path).convert('RGB') as image:
        image_np = np.array(image)
        aspect_ratio = float(image.width)/float(image.height)

        if abs(aspect_ratio-expected_ratio) < threshold :
            crop_height = int(normalised_crop_height * image.height)
            image_no_header = image_np[crop_height:,:]
            image_path = os.path.join(no_manual_revision_tmp, str(time_ns())+'.png')
            new_image = Image.fromarray(image_no_header)
            new_image.save(image_path)
        else:
            essay_information_str = list(map(str, exam_essays_processed.iloc[i]))
            image_filename = '-'.join(essay_information_str) + '_' + str(time_ns())
            image_path = os.path.join(manual_revision_tmp, image_filename+'.png')
            image.save(image_path)

# %%
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload


# %%
def upload_share_png_bytes(filename, bytes_):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'service.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    try:
        service = build('drive', 'v3', credentials=credentials)
        file_metadata = {'name': filename}
        media = MediaIoBaseUpload(bytes_, mimetype='image/png')
        file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()

        permissions = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(
            fileId=file['id'],
            body=permissions).execute()

        return file['id']

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


# %%
def parse_images(image_paths, expected_ratio, threshold, normalised_crop_height,
                 manual_revision_dir,
                 processed_exam_df,
                 base_view_url):

    final_info_list = []
    for i, image_path in enumerate(image_paths):
        with Image.open(image_path).convert('RGB') as image:
            aspect_ratio = float(image.width)/float(image.height)
            essay_info_series = processed_exam_df.iloc[i]

            if abs(aspect_ratio-expected_ratio) < threshold :
                crop_height = int(normalised_crop_height * image.height)
                image_no_header = np.array(image)[crop_height:,:]
                new_image = Image.fromarray(image_no_header)

                image_bytes_object = BytesIO()
                new_image.save(image_bytes_object, 'PNG')
                drive_id = upload_share_png_bytes(str(time_ns())+'.png', image_bytes_object)

                essay_info_series['drive_id'] = drive_id
                essay_info_series['url'] = base_view_url.format(drive_id)
                final_info_list.append(essay_info_series)
            else:
                essay_information_str = list(map(str, essay_info_series))
                image_filename = '-'.join(essay_information_str) + '_' + str(time_ns())
                image_path = os.path.join(manual_revision_dir, image_filename+'.png')
                image.save(image_path)

    final_info_df = pd.concat(final_info_list, axis=1).T
    return final_info_df


# %%
EXPECTED_RATIO = 0.74
THRESHOLD = 0.025
NORMALISED_CROP_HEIGHT = 0.1977
DRIVE_VIEW_BASE_URL = 'https://drive.google.com/file/d/{}/view'
info_df = parse_images(images, EXPECTED_RATIO, THRESHOLD, NORMALISED_CROP_HEIGHT,
                       MANUAL_REVISION_DIR,
                       enem_essays_processed,
                       DRIVE_VIEW_BASE_URL)
info_df

# %%
info_df.url

# %%
for i in range(info_df.shape[0]):
    print(info_df.url.iloc[i])

# %%
info_df.to_csv(OUTPUT_PATH, index=None)

# %%
