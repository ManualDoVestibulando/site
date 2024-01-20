# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: 'Python 3.10.4 (''venv'': venv)'
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Setup

# %%
try:
    from .helper import fix_path
except ImportError:
    from helper import fix_path
fix_path()

# %% [markdown]
# ### Libraries

# %%
from pathlib import Path
from time import time_ns
import os

from PIL import Image
import pandas as pd
import numpy as np

from mdv.config import DataDirectories, EssaysConfig, Exams

# %%
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

# %% [markdown]
# ### Parameters

# %%
INPUT_DIR = DataDirectories.TWO.value / 'redacoes'
OUTPUT_DIR = DataDirectories.THREE.value / 'redacoes'


# %% [markdown]
# ## Helper functions

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
def update_essay_information_dict(exam: str, information: list[str]) -> dict[str, str]:
    if not 2 <= len(information) <= 7:
        raise ValueError('Invalid information list')
    information_dict = {}
    information_dict['ano'] = information[0]
    information_dict['nota'] = information[1]
    if 'enem' in exam.lower():
        for i in range(2, len(information)):
            information_dict[f'c{i-1}'] = information[i]
    return information_dict


# %%
def upload_images(exam: str, image_dir: Path, base_view_url: str) -> pd.DataFrame:

    essay_df_list = []
    for image_path in image_dir.glob('*.png'):
        print(image_path.stem)
        essay_information = image_path.stem.split('_')[0].split('-')
        essay_information_dict = update_essay_information_dict(exam, essay_information)
        with image_path.open('rb') as image_file:
            drive_id = upload_share_png_bytes(image_path.name, image_file)

        essay_information_dict['drive_id'] = drive_id
        essay_information_dict['url'] = base_view_url.format(drive_id)
        essay_df_list.append(pd.Series(essay_information_dict))

    essay_df = pd.concat(essay_df_list, axis=1).T
    return essay_df


# %%
DRIVE_VIEW_BASE_URL = 'https://drive.google.com/file/d/{}/view'

# %%
for exam in Exams:
    exam_name = exam.name.lower()
    exam_input_dir = INPUT_DIR / exam_name / EssaysConfig.YEAR.value / EssaysConfig.NO_REVISION_DIR.value
    print(exam_input_dir)
    exam_output_path = OUTPUT_DIR /  exam_name / (EssaysConfig.YEAR.value+'.csv')
    exam_essay_df = upload_images(exam_name, exam_input_dir, DRIVE_VIEW_BASE_URL)
    exam_essay_df.to_csv(exam_output_path, index=False)
