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
#     display_name: Python 3.10.1 64-bit
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Setup

# %%
import os

import pandas as pd

# %%
FORM_DIR = '../../data/1_initial/forms'
RESULT_DIR = '../../data/2_intermediate/forms'

# %% [markdown]
# ## Reading

# %%
form_list = []
for form_filename in os.listdir(FORM_DIR):
    year = os.path.splitext(form_filename)[0]
    print(year)
    form_path = os.path.join(FORM_DIR, form_filename)
    form_list.append(pd.read_csv(form_path))
print(len(form_list))

# %%
example_form = form_list[0]
print(example_form.columns)
example_form.head()

# %% [markdown]
# ## Parsing

# %% [markdown]
# ### Merging course and institute columns

# %%
example_form.filter(regex='Unidade')

# %%
example_form.filter(regex='Unidade').iloc[0]

# %%
example_form.filter(regex='Unidade').iloc[0].dropna()[0]

# %%
for i in range(example_form.shape[0]):
    print(example_form.filter(regex='Unidade').iloc[i].dropna()[-1])


# %%
def merge_nan_cols(df, col_regex):
    selected_col_df = df.filter(regex=col_regex)
    merged_col_series = selected_col_df.apply((
        lambda x:
            x.dropna()[-1]),
        axis=1)
    return merged_col_series


# %%
unidade_series = merge_nan_cols(example_form, r'^Unidade|unidade \(')
unidade_series

# %%
curso_series = merge_nan_cols(example_form, r'Curso')
curso_series

# %%
unidade_curso_df = pd.DataFrame({
    'unidade': unidade_series,
    'curso': curso_series,
})
unidade_curso_df

# %% [markdown]
# ### Processing results

# %%
example_form['Forma de ingresso'].unique()

# %% [markdown]
# #### Fuvest

# %%
fuvest_mask = example_form['Forma de ingresso'].str.contains('Fuvest')
fuvest_raw = example_form[fuvest_mask]
assert (fuvest_raw['Forma de ingresso'] == 'Fuvest').all()


# %%
def parse_fuvest_results(row):
    return pd.Series({
        'ano':                    row['Qual o seu ano de ingresso?'],
        'modalidade':             row['Modalidade'],
        'chamada':                row['Chamada'],
        'nota_1':                 row['Nota na 1° fase'],
        'nota_2_1':               row['Nota na 2° fase, 1° dia'],
        'nota_2_2':               row['Nota na 2° fase, 2° dia'],
        'nota_final':             row['Nota final'],
        'nota_redacao':           row['Nota da redação'],
        'classificacao_carreira': row['Classificação na carreira'],
        'classificacao_curso':    row['Classificação no curso de ingresso'],
        'redacao':                row['Envie aqui o espelho da sua redação'],
    })

fuvest_data = fuvest_raw.apply(parse_fuvest_results, axis=1)
fuvest_data.head()

# %%
fuvest_results = pd.concat([unidade_curso_df[fuvest_mask], fuvest_data], axis=1)
fuvest_results.head()

# %% [markdown]
# #### Enem

# %%
enem_mask = example_form['Forma de ingresso'].str.contains('Enem')
enem_raw = example_form[enem_mask]
assert (enem_raw['Forma de ingresso'] == 'SiSU (Enem)').all()


# %%
def parse_enem_results(row):
    return pd.Series({
        'ano':             row['Qual o seu ano de ingresso?'],
        'modalidade':      row['Modalidade'],
        'chamada':         row['Chamada'],
        'nota_linguagens': row['Linguagens'],
        'nota_humanas':    row['Ciências Humanas'],
        'nota_natureza':   row['Ciências da Natureza'],
        'nota_matematica': row['Matemática'],
        'nota_redacao':    row['Redação'],
        'nota_final':      row['Nota final.1'],
        'nota_redacao_c1': row['Nota na Competência 1'],
        'nota_redacao_c2': row['Nota na Competência 2'],
        'nota_redacao_c3': row['Nota na Competência 3'],
        'nota_redacao_c4': row['Nota na Competência 4'],
        'nota_redacao_c5': row['Nota na Competência 5'],
        'redacao':         row['Envie aqui o espelho da sua redação.1'],
    })

enem_data = enem_raw.apply(parse_enem_results, axis=1)
enem_data.head()

# %%
enem_results = pd.concat([unidade_curso_df[enem_mask], enem_data], axis=1)
enem_results.head()

# %% [markdown]
# ## Merging all collected data

# %%
for form_filename in os.listdir(FORM_DIR):
    form_path = os.path.join(FORM_DIR, form_filename)
    form_df = pd.read_csv(form_path)

    unidade_series = merge_nan_cols(form_df,
        r'^Unidade|unidade \(')
    curso_series = merge_nan_cols(form_df,
        r'Curso')
    unidade_curso_df = pd.DataFrame({
        'unidade': unidade_series,
        'curso': curso_series,
    })

    fuvest_mask = form_df['Forma de ingresso'].str.contains('Fuvest')
    enem_mask = form_df['Forma de ingresso'].str.contains('Enem')

    fuvest_raw = form_df[fuvest_mask]
    enem_raw = form_df[enem_mask]

    fuvest_data = fuvest_raw.apply(parse_fuvest_results, axis=1)
    enem_data = enem_raw.apply(parse_enem_results, axis=1)

    fuvest = pd.concat([unidade_curso_df[fuvest_mask], fuvest_data],
                       axis=1)
    enem = pd.concat([unidade_curso_df[enem_mask], enem_data],
                     axis=1)

    fuvest.convert_dtypes().to_csv(os.path.join(RESULT_DIR, 'fuvest', form_filename), index=None) 
    enem.convert_dtypes().to_csv(os.path.join(RESULT_DIR, 'enem', form_filename), index=None) 

# %%
