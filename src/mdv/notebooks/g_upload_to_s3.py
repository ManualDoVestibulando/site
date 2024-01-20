# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: 'Python 3.10.5 (''venv'': venv)'
#     language: python
#     name: python3
# ---

# %%
try:
    from .helper import fix_path
except ImportError:
    from helper import fix_path
fix_path()

# %% [markdown]
# ## Setup

# %%
import json
import mimetypes
from pathlib import Path
from typing import Callable
from threading import Thread

import boto3

from mdv.config import REPOSITORY_ROOT

# %%
PARALLEL_THREADS = 40

WEBSITE_DIR_NAME = 'website/'
WEBSITE_PATH = REPOSITORY_ROOT / WEBSITE_DIR_NAME

AWS_JSON_PATH = REPOSITORY_ROOT / 'aws.json'
BUCKET_NAME = 'manual-do-vestibulando'


# %% [markdown]
# ## Support functions

# %%
def get_s3_client(json_path: str) -> boto3.Session:
    with open(json_path, 'r', encoding='utf8') as f:
        credentials_dict = json.loads(f.read())
    return boto3.client(
        's3',
        aws_access_key_id=credentials_dict['key'],
        aws_secret_access_key=credentials_dict['secret'],
        region_name=credentials_dict['region'],
    )


# %%
def recursive_list(root: Path) -> list[Path]:
    filepaths = []
    for path in root.iterdir():
        if path.is_dir():
            filepaths.extend(recursive_list(path))
        else:
            filepaths.append(path)

    return filepaths


# %% [markdown]
# ## Upload

# %%
s3 = get_s3_client(AWS_JSON_PATH)


# %%
def upload_to_s3(
        filepath: Path,
        website_dir: str,
        bucket_name: str,
        s3) -> None:
    extra_args = {'ContentType': mimetypes.guess_type(filepath)[0]}
    s3_object_name = str(filepath).split(website_dir)[1]
    s3.upload_file(
        str(filepath), # S3 only supports string paths
        bucket_name,
        s3_object_name,
        ExtraArgs=extra_args,
    )
    print(f'Uploaded from {filepath} to s3://{bucket_name}/{s3_object_name}')


# %%
website_filepaths = recursive_list(WEBSITE_PATH)
website_filepaths

# %%
NUMBER_GROUPS = (len(website_filepaths) // PARALLEL_THREADS) + 1

grouped_website_filepaths = [
    website_filepaths[i*PARALLEL_THREADS:(i+1)*PARALLEL_THREADS]
    for i in range(NUMBER_GROUPS)
]
grouped_website_filepaths

# %%
for filepath_group in grouped_website_filepaths:
    threads = [
        Thread(
            target=upload_to_s3,
            args=(
                filepath,
                WEBSITE_DIR_NAME,
                BUCKET_NAME,
                s3,
            ),
        )
        for filepath in filepath_group
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
