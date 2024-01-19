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

# %% [markdown]
# ### Parameters

# %%
ENEM_ESSAYS_DIR = (DataDirectories.ONE.value / 'redacoes'
                 / Exams.ENEM.name.lower() / EssaysConfig.YEAR.value)
FUVEST_ESSAYS_DIR = (DataDirectories.ONE.value / 'redacoes'
                    / Exams.FUVEST.name.lower() / EssaysConfig.YEAR.value)
ENEM_FORM_PATH = (DataDirectories.TWO.value / 'forms'
                / Exams.ENEM.name.lower() / (EssaysConfig.YEAR.value+'.csv'))
FUVEST_FORM_PATH = (DataDirectories.TWO.value / 'forms'
                / Exams.FUVEST.name.lower() / (EssaysConfig.YEAR.value+'.csv'))

# %%
OUTPUT_DIR = DataDirectories.TWO.value / 'redacoes'


# %% [markdown]
# ## Helper functions

# %%
def listdir_sorted(dir: Path) -> tuple[Path]:
    paths = list(dir.iterdir())
    # TODO Test getctime instead of getmtime
    paths.sort(key=os.path.getmtime)
    return tuple(paths)


# %%
def get_essays(form_df: pd.DataFrame,
        essay_column_name: str = 'redacao') -> pd.DataFrame:
    essay_mask = np.logical_not(form_df[essay_column_name].isna())
    exam_essays = form_df.loc[essay_mask]
    return exam_essays


# %% [markdown]
# ## Enem

# %% [markdown]
# ### Reading

# %%
enem_form_df = pd.read_csv(ENEM_FORM_PATH)
enem_form_df.head()

# %%
enem_images = listdir_sorted(ENEM_ESSAYS_DIR)
print(len(enem_images))
enem_images[:5]

# %%
enem_essays = get_essays(enem_form_df)
print(enem_essays.shape)
enem_essays


# %% [markdown]
# ### Parsing

# %%
def parse_enem_essays(row):
    return pd.Series({
        'ano':  row['ano'],
        'nota': row['nota_redacao'],
        'c1':   row['nota_redacao_c1'],
        'c2':   row['nota_redacao_c2'],
        'c3':   row['nota_redacao_c3'],
        'c4':   row['nota_redacao_c4'],
        'c5':   row['nota_redacao_c5'],
    })

enem_essays_processed = enem_essays.apply(parse_enem_essays,
                                          axis=1)\
                                   .convert_dtypes()
enem_essays_processed['filepath'] = enem_images
enem_essays_processed

# %% [markdown]
# ## Fuvest

# %% [markdown]
# ### Reading

# %%
fuvest_form_df = pd.read_csv(FUVEST_FORM_PATH)
fuvest_form_df.head()

# %%
fuvest_images = listdir_sorted(FUVEST_ESSAYS_DIR)
print(len(fuvest_images))
fuvest_images[:5]

# %%
fuvest_essays = get_essays(fuvest_form_df)
print(fuvest_essays.shape)
fuvest_essays


# %% [markdown]
# ### Parsing

# %%
def parse_fuvest_essays(row):
    return pd.Series({
        'ano':  row['ano'],
        'nota': row['nota_redacao'],
    })

fuvest_essays_processed = fuvest_essays.apply(parse_fuvest_essays,
                                            axis=1)\
                                       .convert_dtypes()
fuvest_essays_processed['filepath'] = fuvest_images
fuvest_essays_processed

# %%
print(fuvest_essays_processed.iloc[-1].filepath)
fuvest_essays_processed.iloc[-1]

# %% [markdown]
# ## Processing

# %%
essays: dict[str, pd.DataFrame] = {
    Exams.ENEM.name.lower(): enem_essays_processed,
    Exams.FUVEST.name.lower(): fuvest_essays_processed
}
essays

# %%
for exam in Exams:
    exam_name = exam.name.lower()

    exam_output_dir = OUTPUT_DIR / exam_name / EssaysConfig.YEAR.value
    exam_revision_dir = exam_output_dir / EssaysConfig.REVISION_DIR.value
    exam_no_revision_dir = exam_output_dir / EssaysConfig.NO_REVISION_DIR.value
    exam_revision_dir.mkdir(parents=True, exist_ok=True)
    exam_no_revision_dir.mkdir(parents=True, exist_ok=True)

    exam_df = essays[exam_name]
    exam_images = exam_df.filepath
    expected_ratio = EssaysConfig.ASPECT_RATIO.value[exam_name]
    threshold = EssaysConfig.THRESHOLD.value[exam_name]
    normalized_crop_height = EssaysConfig.NORMALIZED_CROP_HEIGHT.value[exam_name]

    for _, row in exam_df.iterrows():
        image_path = row.filepath
        essay_data = row.drop('filepath')
        with Image.open(image_path).convert('RGB') as image:
            image_np = np.array(image)
            aspect_ratio = float(image.width)/float(image.height)

            if abs(aspect_ratio-expected_ratio) < threshold :
                crop_height = int(normalized_crop_height * image.height)
                image_no_header = image_np[crop_height:,:]
                new_image = Image.fromarray(image_no_header)
                image_dir = exam_no_revision_dir
            else:
                new_image = image
                image_dir = exam_revision_dir

            essay_information_str = list(map(str, essay_data))
            image_filename = '-'.join(essay_information_str) + '_' + str(time_ns())
            image_path = image_dir / (image_filename+'.png')
            new_image.save(image_path)
