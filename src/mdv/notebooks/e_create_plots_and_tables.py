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
#     display_name: Python 3
#     name: python3
# ---

# %% tags=["parameters"]

# %% id="DuZ9D3RvZtJo"
import os

import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# %% id="QSI1tOa2Z-4A"
INPUT_PATH = '../../data/4_final/forms'
OUTPUT_PATH = '../../data/5_content'

# %% [markdown] id="HUixgzJbeG4y"
# ## Reading

# %% colab={"base_uri": "https://localhost:8080/", "height": 478} id="Ul6nEbWvZ0k7" outputId="04f7baa7-3b32-4593-948f-0b4d3cff9eb8"
enem = pd.read_csv(os.path.join(INPUT_PATH, 'enem.csv')).convert_dtypes()
enem.head()

# %% colab={"base_uri": "https://localhost:8080/", "height": 392} id="GVyPBuqhaQfh" outputId="d060c8ee-af15-48c8-860b-192c8e7aca47"
fuvest = pd.read_csv(os.path.join(INPUT_PATH, 'fuvest.csv')).convert_dtypes()
fuvest.head()


# %% [markdown] id="SV1juRo9eK5G"
# ## Analysing

# %% [markdown] id="SRDEfmRDxKXR"
# ### Support functions

# %% id="yjSGGgkKxMMS"
def table_from_df(df, cols=None, manual_header=None, cells_format=None):
  if cols is None:
    cols = df.columns

  if manual_header is not None:
    header_values = manual_header
  else:
    header_values = cols

  data_list = [df[col] for col in cols]
  fig = go.Figure(data=go.Table(
      header=dict(values=header_values,
                  align='center'),
      cells=dict(values=data_list,
                 format=cells_format),
  ))
  return fig


# %% id="6knHEEmKR7GF"
def plotly_fig_to_html(fig, path):
  fig.update_layout(margin=dict(
      b=0,
      l=0,
      r=0,
      t=0,
  ))
  fig.write_html(path, include_plotlyjs='cdn', full_html=False)


# %% [markdown] id="5u1YDsnweQE5"
# ### Fuvest

# %% id="AhTt3k_hNeo9"
for index, row in fuvest[['id', 'ano']].drop_duplicates().iterrows():
  os.makedirs(os.path.join(OUTPUT_PATH, str(row.id), 'fuvest', str(row.ano)))

# %% colab={"base_uri": "https://localhost:8080/"} id="atQcpoLOacP6" outputId="27197c86-dc23-4af5-e8f0-df165a564f41"
fuvest_grouped = fuvest.groupby(['id', 'ano', 'modalidade'])
fuvest_grouped.groups

# %% colab={"base_uri": "https://localhost:8080/", "height": 455} id="laWfawLaawJh" outputId="181a0ede-20c7-466f-b4c0-d20441cee1e4"
fuvest_metrics_df = fuvest_grouped.agg(
  Mínimo=('nota_final', 'min'),
  Máximo=('nota_final', 'max'),
  Médio=('nota_final', 'mean'),
)
fuvest_metrics_df

# %% [markdown] id="Lar2h-t9Qg0-"
# #### Metrics plot

# %% colab={"base_uri": "https://localhost:8080/", "height": 238} id="kZC-Y8-k1z5O" outputId="cc3c0024-06b0-4bfe-d69d-0c3ddf77f92b"
example_metrics = fuvest_metrics_df.loc[0].reset_index()
example_metrics

# %% colab={"base_uri": "https://localhost:8080/", "height": 614} id="WkVijELW_yh2" outputId="47bad51c-f8e1-4d72-ce68-fb119f02fe13"
molten_example_metrics = pd.melt(example_metrics,
                                 id_vars=['ano', 'modalidade'],
                                 value_vars=['Mínimo', 'Médio', 'Máximo'],
                                 var_name='metric',
                                 value_name='nota')
molten_example_metrics

# %% colab={"base_uri": "https://localhost:8080/"} id="YZIBwEDzt9Ox" outputId="64f84af0-6a00-40df-a817-dda41ee5a9e6"
first_year = molten_example_metrics.ano.min()
first_year

# %% colab={"base_uri": "https://localhost:8080/", "height": 542} id="ABtSDZZQ6Snf" outputId="d44464f6-8d59-480a-a91e-3e2178bd939c"
px.line(
  molten_example_metrics,
  x='ano', y='nota',
  color='metric',
  facet_row='modalidade',
  markers=True,

  labels={
      'ano': 'Ano de ingresso',
      'nota': '',
      'metric': 'Valor',
  },
  category_orders={
      'modalidade': ['Ampla Concorrência (AC)',
                     'Escola Pública (EP)',
                     'Pretos, Pardos e Indígenas (PPI)'],
      'metric': ['Máximo', 'Médio', 'Mínimo'],
  },
)


# %% colab={"base_uri": "https://localhost:8080/", "height": 560} id="wOl0I3j4PqX-" outputId="f599b467-4c1e-4b70-d601-a4fc1aa82f66"
def abbreviate_quota(plotly_annotation):
  text = plotly_annotation.text
  new_text = text
  for abbreviation in ['AC', 'EP', 'PPI']:
    if abbreviation in text:
      new_text = abbreviation
      break

  return plotly_annotation.update(text=new_text)

figs = []
for id, df in fuvest_metrics_df.groupby('id'):
  molten_df = pd.melt(df.reset_index(),
                      id_vars=['ano', 'modalidade'],
                      value_vars=['Mínimo', 'Máximo', 'Médio'],
                      var_name='metric',
                      value_name='nota')
  fig = px.line(
    molten_df,
    x='ano', y='nota',
    color='metric',
    facet_row='modalidade',
    markers=True,

    labels={
        'ano': 'Ano de ingresso',
        'nota': '',
        'metric': 'Valor',
    },
    category_orders={
        'modalidade': ['Ampla Concorrência (AC)',
                      'Escola Pública (EP)',
                      'Pretos, Pardos e Indígenas (PPI)'],
        'metric': ['Máximo', 'Médio', 'Mínimo'],
    },
  )
  first_year = molten_df.ano.min()
  fig.update_layout(
      xaxis=dict(
          tickmode='linear',
          tick0=first_year,
          dtick=1,
          fixedrange=True,
      ),
      yaxis=dict(
          fixedrange=True,
      ),
  )
  fig.for_each_annotation(abbreviate_quota)

  figs.append(fig)

print(len(figs))
figs[0].show()

# %% colab={"base_uri": "https://localhost:8080/", "height": 542} id="j4hX6lrPAdab" outputId="ecfc02c4-ac74-43e6-89c6-68ea882c3a23"
figs[102].show()


# %% id="Kh0YD9JdQVuB"
def plot_metric_evolution(metrics_df, exam='fuvest'):

  def abbreviate_quota(plotly_annotation):
    text = plotly_annotation.text
    new_text = text
    for abbreviation in ['AC', 'EP', 'PPI']:
      if abbreviation in text:
        new_text = abbreviation
        break

    return plotly_annotation.update(text=new_text)

  for id, df in metrics_df.groupby('id'):
    molten_df = pd.melt(df.reset_index(),
                        id_vars=['ano', 'modalidade'],
                        value_vars=['Mínimo', 'Máximo', 'Médio'],
                        var_name='metric',
                        value_name='nota')
    fig = px.line(
      molten_df,
      x='ano', y='nota',
      color='metric',
      facet_row='modalidade',
      markers=True,

      labels={
          'ano': 'Ano de ingresso',
          'nota': '',
          'metric': 'Valor',
      },
      category_orders={
          'modalidade': ['Ampla Concorrência (AC)',
                        'Escola Pública (EP)',
                        'Pretos, Pardos e Indígenas (PPI)'],
          'metric': ['Máximo', 'Médio', 'Mínimo'],
      },
    )
    first_year = molten_df.ano.min()
    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=first_year,
            dtick=1,
            fixedrange=True,
        ),
        yaxis=dict(
            fixedrange=True,
        ),
    )
    fig.for_each_annotation(abbreviate_quota)

    plotly_fig_to_html(
      fig,
      os.path.join(OUTPUT_PATH, str(id), exam,
                   'metric_evolution.html'))


# %% id="HLiHOvQkRSnB"
plot_metric_evolution(fuvest_metrics_df)

# %% [markdown] id="EbdflwE3Qk5a"
# #### Metrics table for the latest year

# %% colab={"base_uri": "https://localhost:8080/"} id="wFBBtcTPp_vA" outputId="cbff5066-417a-4dcb-d1c9-8c902bbf3467"
for id, df in fuvest_metrics_df.reset_index().groupby('id'):
  print(id)
  print(df[['ano', 'modalidade', 'Mínimo', 'Médio', 'Máximo']])

# %% colab={"base_uri": "https://localhost:8080/", "height": 560} id="YrLvVeq_MN0X" outputId="77c4db96-a407-4a50-ba89-56edfb14dded"
metric_tables = []
# TODO add latest avaliable year to the title of the table
for id, df in fuvest_metrics_df.reset_index().groupby('id'):
  latest_metrics_df = df.loc[df.ano == df.ano.max()]
  metric_tables.append(table_from_df(latest_metrics_df,
                                     ['modalidade', 'Mínimo', 'Médio', 'Máximo'],
                                     ['Modalidade', 'Mínima', 'Média', 'Máxima'],
                                     [None, '.2f', '.2f', '.2f']))

print(len(metric_tables))
metric_tables[0].show()

# %% colab={"base_uri": "https://localhost:8080/", "height": 542} id="kshpbcr90cxC" outputId="1a8d7571-4db3-4c84-e932-7dfd2f864882"
metric_tables[45].show()


# %% id="K3vIUQYTRkaA"
def plot_latest_metrics_table(metrics_df, exam='fuvest'):
  # TODO add latest avaliable year to the title of the table
  for id, df in metrics_df.reset_index().groupby('id'):
    latest_metrics_df = df.loc[df.ano == df.ano.max()]
    plotly_fig_to_html(
      table_from_df(latest_metrics_df,
                    ['modalidade', 'Mínimo', 'Médio', 'Máximo'],
                    ['Modalidade', 'Mínima', 'Média', 'Máxima'],
                    [None, '.2f', '.2f', '.2f']),
      os.path.join(OUTPUT_PATH, str(id), exam,
                   'latest_metrics.html'))


# %% id="ZsUpOV2fSk5B"
plot_latest_metrics_table(fuvest_metrics_df)

# %% [markdown] id="-BJxEYQjQqgt"
# #### Data tables

# %% colab={"base_uri": "https://localhost:8080/", "height": 560} id="oRsXXlnnBv4p" outputId="fb59ffd6-666b-4450-86c6-0a5cb42c8387"
TABLE_COL_NAMES = [
  'chamada',
  'nota_1',
  'nota_2_1',
  'nota_2_2',
  'nota_final',
  'nota_redacao',
  'classificacao_carreira',
  'classificacao_curso',
]
HEADER_COL_NAMES = [
  'Chamada',
  '1° fase',
  '2° fase, 1° dia',
  '2° fase, 2° dia',
  'Nota final',
  'Nota da redação',
  'Classificação na carreira',
  'Classificação no curso',
]
COL_FORMATS = [None, None, '.2f', '.2f', '.2f', '.1f', None, None]
data_tables = []

for id, df in fuvest.groupby('id'):
  df = df.reset_index()
  for ano in df['ano'].unique():
    for modalidade in df['modalidade'].unique():
      sliced_df = df[(df['ano'] == ano)
                     & (df['modalidade'] == modalidade)]
      if not sliced_df.empty:
        sliced_df = sliced_df.sort_values('nota_final', ascending=False)
        full_df = sliced_df.astype(str)
        data_tables.append(table_from_df(full_df,
                                         TABLE_COL_NAMES,
                                         HEADER_COL_NAMES,
                                         COL_FORMATS))
print(len(data_tables))
data_tables[0].show()


# %% id="R7BiT2I6Dl4A"
def plot_data_tables(exam_df, cols, header, cells_format, exam='fuvest'):
  for id, df in exam_df.groupby('id'):
    df = df.reset_index()
    for ano in df['ano'].unique():
      for modalidade in df['modalidade'].unique():
        sliced_df = df[(df['ano'] == ano)
                      & (df['modalidade'] == modalidade)]
        if not sliced_df.empty:
          sliced_df = sliced_df.sort_values('nota_final', ascending=False)
          full_df = sliced_df.astype(str)
          plotly_fig_to_html(
            table_from_df(full_df, cols, header, cells_format),
            os.path.join(OUTPUT_PATH, str(id), exam,
                         str(ano), f'{modalidade}.html')
          )


# %% id="2ClaiKpNUUPq"
plot_data_tables(fuvest, TABLE_COL_NAMES, HEADER_COL_NAMES, COL_FORMATS)

# %% [markdown] id="XAGWr2lwH_3F"
# ### Enem

# %% id="exX5crdzH90O"
for index, row in enem[['id', 'ano']].drop_duplicates().iterrows():
  os.makedirs(os.path.join(OUTPUT_PATH, str(row.id), 'enem', str(row.ano)))

# %% colab={"base_uri": "https://localhost:8080/"} id="zBoqmK_sIovD" outputId="923ceb25-2a83-4571-90ce-e2ce14c5597f"
enem_grouped = enem.groupby(['id', 'ano', 'modalidade'])
enem_grouped.groups

# %% colab={"base_uri": "https://localhost:8080/", "height": 455} id="Sbvkr2H_IscW" outputId="cc895dbd-dac9-4253-8eff-03459605bc7b"
enem_metrics_df = enem_grouped.agg(
  Mínimo=('nota_final', 'min'),
  Máximo=('nota_final', 'max'),
  Médio=('nota_final', 'mean'),
)
enem_metrics_df

# %% [markdown] id="c7nmj1wRJVWG"
# #### Metrics plot

# %% id="uvB19k5jJXMR"
plot_metric_evolution(enem_metrics_df, exam='enem')

# %% [markdown] id="-5Z8re_YJek_"
# #### Metrics table for the latest year

# %% id="A9__x452JiA6"
plot_latest_metrics_table(enem_metrics_df, exam='enem')

# %% [markdown] id="euOIApzyJy2c"
# #### Data tables

# %% colab={"base_uri": "https://localhost:8080/"} id="wAt6u6thKvFL" outputId="c22fcf39-9a47-49d3-aa91-1b240781a9ab"
enem.columns

# %% id="Pi9dzfvqJ1Po"
ENEM_TABLE_COL_NAMES = [
  'chamada',
  'nota_linguagens',
  'nota_humanas',
  'nota_natureza',
  'nota_matematica',
  'nota_redacao',
  'nota_final',
]
ENEM_HEADER_COL_NAMES = [
  'Chamada',
  'Linguagens',
  'Humanas',
  'Ciências da Natureza',
  'Matemática',
  'Nota da redação',
  'Nota final',
]
ENEM_COL_FORMATS = [None, '.2f', '.2f', '.2f', '.2f', '.3d', '.2f']

plot_data_tables(enem,
                 ENEM_TABLE_COL_NAMES,
                 ENEM_HEADER_COL_NAMES,
                 ENEM_COL_FORMATS,
                 exam='enem')

# %% id="HBNO1IRirrCP"
