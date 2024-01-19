# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3.10.1 ('mdv')
#     language: python
#     name: python3
# ---

# %%
import pandas as pd

# %%
FORM_PATH = '/home/tomaz/Desktop/MDV/anglo.csv'
RESULT_PATH = '/home/tomaz/Desktop/MDV/anglo_processed.csv'

VACCANCIES_PATH = '../../data/4_final/vagas/2022.csv'

# %% [markdown]
# ## Reformatting Anglo's data

# %%
anglo_raw = pd.read_csv(FORM_PATH)
anglo_raw

# %%
anglo_raw.columns


# %%
def parse_fuvest_results(row):

    return pd.Series({
        'id':                     row['id'],
        'ano':                    2022,
        'modalidade':             row['MODALIDADE'],
        'chamada':                'Primeira',
        'nota_1':                 row['ACERTOS NA 1ª FASE'],
        'nota_2_1':               row['NOTA NA 2ª FASE (1º DIA)'],
        'nota_2_2':               row['NOTA NA 2ª FASE (2º DIA)'],
        'nota_final':             row['NOTA FINAL'],
        'nota_redacao':           row['REDAÇÃO'],
        'classificacao_carreira': pd.NA,
        'classificacao_curso':    row['CLASSIFICAÇÃO NA CARREIRA NA MODALIDADE DE INGRESSO'],
        'redacao':                pd.NA,
    })

anglo_data = anglo_raw.apply(parse_fuvest_results, axis=1)
anglo_data.head()

# %%
anglo_data.isna().sum()

# %%
filter = anglo_data.modalidade.isna() | anglo_data.classificacao_curso.isna()
anglo_data.loc[filter][['modalidade', 'classificacao_curso']]

# %%
clean_anglo_data = anglo_data.dropna(thresh=9)
clean_anglo_data

# %%
clean_anglo_data.isna().sum()

# %%
full_modalidade_dict = {
    'EP': 'Escola Pública (EP)',
    'AC': 'Ampla Concorrência (AC)',
    'PPI': 'Pretos, Pardos e Indígenas (PPI)',
}

clean_anglo_data.modalidade.replace(full_modalidade_dict, inplace=True)
clean_anglo_data

# %% [markdown]
# ## Adding MDV course information

# %%
vaccancies = pd.read_csv(VACCANCIES_PATH)
vaccancies

# %%
full_anglo_data = vaccancies[['id', 'unidade', 'curso']].merge(clean_anglo_data,
                                                               on='id',
                                                               validate='1:m')
full_anglo_data

# %%
full_anglo_data.to_csv(RESULT_PATH, index=None)
