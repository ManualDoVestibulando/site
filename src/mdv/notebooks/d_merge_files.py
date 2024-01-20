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

# %%
try:
    from .helper import fix_path
except ImportError:
    from helper import fix_path
fix_path()

# %%
import os
import shutil

import pandas as pd

from mdv.config import DataDirectories

# %%
were_files_manually_reviewed = True

# %%
if not were_files_manually_reviewed:
    raise Exception('Files must be manually reviewed and review '
                   +'results copied to 3_processed/ before proceeding')

# %%
FORM_INPUT_PATH = DataDirectories.THREE.value / 'forms'
FORM_OUTPUT_PATH = DataDirectories.FOUR.value / 'forms'
VACANCIES_INPUT_PATH = DataDirectories.THREE.value / 'vagas'
VACANCIES_OUTPUT_PATH = DataDirectories.FOUR.value
ESSAY_INPUT_PATH = DataDirectories.THREE.value / 'redacoes'
ESSAY_OUTPUT_PATH = DataDirectories.FOUR.value / 'redacoes'

# %% [markdown]
# ## Forms

# %%
for exam in os.listdir(FORM_INPUT_PATH):
    exam_forms_list = []
    exam_dir = os.path.join(FORM_INPUT_PATH, exam)
    if os.path.isdir(exam_dir):
        for form in os.listdir(exam_dir):
            form_path = os.path.join(exam_dir, form)
            form_df = pd.read_csv(form_path)
            exam_forms_list.append(form_df)
        exam_forms_df = pd.concat(exam_forms_list)
        exam_forms_df.to_csv(os.path.join(FORM_OUTPUT_PATH, exam + '.csv'), index=False)

# %% [markdown]
# ## Vacancies

# %%
latest_vacancies_filename = sorted(os.listdir(VACANCIES_INPUT_PATH))[-1]
latest_vacancies_path = os.path.join(VACANCIES_INPUT_PATH, latest_vacancies_filename)
output_vacancies_filename = os.path.join(VACANCIES_OUTPUT_PATH, 'vagas.csv')
shutil.copy(latest_vacancies_path, output_vacancies_filename)

# %% [markdown]
# ## Essays

# %%
for exam in os.listdir(ESSAY_INPUT_PATH):
    exam_essays_list = []
    exam_dir = os.path.join(ESSAY_INPUT_PATH, exam)
    if os.path.isdir(exam_dir):
        for essays in os.listdir(exam_dir):
            essays_path = os.path.join(exam_dir, essays)
            essays_df = pd.read_csv(essays_path)
            exam_essays_list.append(essays_df)
        exam_essays_df = pd.concat(exam_essays_list)
        exam_essays_df.to_csv(os.path.join(ESSAY_OUTPUT_PATH, exam + '.csv'), index=False)
