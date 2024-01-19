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

# %% tags=["parameters"]

# %% [markdown]
# ## Setup

# %%
from os import listdir, makedirs
from os.path import join, isdir, splitext
from unidecode import unidecode

from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas as pd

# %%
TEMPLATES_DIR = '../../templates'
CONTENT_DIR = '../../data/5_content'
GRADES_RESULT_DIR = '../../website/notas'

ID_TABLE_PATH = '../../data/4_final/vagas.csv'
ESSAYS_DIR = '../../data/4_final/redacoes'
ESSAYS_RESULT_DIR = '../../website/redacoes'


# %% [markdown]
# ## Support functions

# %%
def clean_string(string):
    alphanumerical_chars = [char for char in string if char.isalnum()]
    return unidecode("".join(alphanumerical_chars))


# %%
def get_course_name(course_id, id_df):
    return id_df[id_df.id == course_id].curso.iloc[0]


# %%
def get_course_institute(course_id, id_df):
    return id_df[id_df.id == course_id].unidade.iloc[0]


# %%
def get_course_name_institute(course_id, id_df):
    name = get_course_name(course_id, id_df)
    institure = get_course_institute(course_id, id_df)
    return name, institure


# %%
def create_render_save_path(result_dir=None, course_id=None,
                            new_dir=None, filename=None,
                            id_df=None):
    save_dir = ''
    if result_dir is not None and course_id is not None:
        save_dir = join(result_dir, str(course_id))
    if new_dir is not None:
        save_dir = join(save_dir, new_dir)
        makedirs(save_dir, exist_ok=True)
    if filename is None and id_df is not None:
        filename = get_course_name(course_id, id_df)
    clean_filename = clean_string(filename)

    return join(save_dir, clean_filename+'.html')


# %%
def save_website(website, path):
    with open(path, mode='w') as f:
        f.write(website)


# %%
def read_file_content(filepath):
    with open(filepath, mode='r') as f:
        return f.read()


# %%
def parse_content(path):
    latest_metrics_plotly_div = read_file_content(join(path, 'latest_metrics.html'))
    metric_evolution_plotly_div = read_file_content(join(path, 'metric_evolution.html'))
    grade_dict = {}
    for year in listdir(path):
        year_dict = {}
        year_dir = join(path, year)
        if isdir(year_dir):
            for quota_filename in listdir(year_dir):
                quota, _ = splitext(quota_filename)
                year_dict[quota] = read_file_content(join(year_dir, quota_filename))
            grade_dict[year] = year_dict

    return (latest_metrics_plotly_div,
            metric_evolution_plotly_div,
            grade_dict)


# %% [markdown]
# ## Rendering

# %%
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape())

# %% [markdown]
# ### Grades

# %%
ID_DF = pd.read_csv(ID_TABLE_PATH).convert_dtypes()
print(ID_DF.dtypes)
ID_DF

# %%
get_course_name(0, ID_DF)


# %% [markdown]
# #### Courses

# %%
def read_course_templates(jinja_env,
                          template_filename='notas.html.jinja'):
    return jinja_env.get_template(template_filename)


# %%
for course_id_str in listdir(CONTENT_DIR):
    if isdir(join(CONTENT_DIR, course_id_str)):
        course_id = int(course_id_str)
        course_name = get_course_name(course_id, ID_DF)
        print(course_name)


# %% [markdown]
# #### Exam selection

# %%
def render_selection(jinja_env, result_dir, course_id,
                     course_name=None, id_df=None,
                     fuvest=False, enem=False,
                     fuvest_url=None, enem_url=None,
                     template_filename='vestibulares.html.jinja',
                     render_filename='vestibulares'):
    if course_name is None:
        course_name = get_course_name(course_id, id_df)
    selection_template = jinja_env.get_template(template_filename)
    selection_website = selection_template.render(
        active_link='Notas',
        root_path='../../',
        course_name=course_name,
        render_fuvest=fuvest,
        render_enem=enem,
        fuvest_url=fuvest_url,
        enem_url=enem_url,
        button_text='Acesse as notas')
    selection_path = create_render_save_path(
        result_dir=result_dir,
        course_id=course_id,
        filename=render_filename,
    )
    save_website(selection_website, selection_path)


# %% [markdown]
# #### Course selection

# %%
def render_course_selection(jinja_env, result_dir,
                            all_courses_dict=None,
                            template_filename='cursos.html.jinja',
                            render_filename='cursos'):
    courses_template = jinja_env.get_template(template_filename)
    courses_website = courses_template.render(
        active_link='Notas',
        root_path='../',
        all_courses_dict=all_courses_dict)
    courses_path = join(result_dir, render_filename+'.html')
    save_website(courses_website, courses_path)


# %% [markdown]
# #### Final rendering

# %%
def render_courses(content_dir, jinja_env, id_df, result_dir):
    course_template = read_course_templates(jinja_env)
    all_courses_dict = {}

    for course_id_str in listdir(content_dir):
        render_fuvest = False
        render_enem = False

        course_dir = join(content_dir, course_id_str)
        if isdir(course_dir):
            course_id = int(course_id_str)
            course_name, course_institute = get_course_name_institute(course_id, id_df)
            all_courses_dict[f'{course_institute} - {course_name}'] = join(course_id_str, 'vestibulares.html')

            for exam in listdir(course_dir):
                if exam == 'fuvest':
                    render_fuvest = True
                    fuvest_dir = join(course_dir, 'fuvest')
                    latest_metrics, metric_evolution, grade_dict = parse_content(fuvest_dir)
                    fuvest_website = course_template.render(
                        active_link='Notas',
                        root_path='../../../',
                        course_name=course_name,
                        latest_metrics_plotly_div=latest_metrics,
                        metric_evolution_plotly_div=metric_evolution,
                        grade_dict=grade_dict)
                    fuvest_path = create_render_save_path(
                        result_dir=result_dir,
                        course_id=course_id,
                        new_dir='fuvest',
                        filename=course_name,
                    )
                    save_website(fuvest_website, fuvest_path)
                elif exam == 'enem':
                    render_enem = True
                    enem_dir = join(course_dir, 'enem')
                    latest_metrics, metric_evolution, grade_dict = parse_content(enem_dir)
                    enem_website = course_template.render(
                        active_link='Notas',
                        root_path='../../../',
                        course_name=course_name,
                        latest_metrics_plotly_div=latest_metrics,
                        metric_evolution_plotly_div=metric_evolution,
                        grade_dict=grade_dict)
                    enem_path = create_render_save_path(
                        result_dir=result_dir,
                        course_id=course_id,
                        new_dir='enem',
                        filename=course_name,
                    )
                    save_website(enem_website, enem_path)
                else:
                    raise ValueError(f'Unknown exam type inside directory {course_dir}.')

            render_selection(jinja_env, result_dir, course_id, course_name,
                             fuvest=render_fuvest, enem=render_enem,
                             fuvest_url=create_render_save_path(new_dir='fuvest', filename=course_name),
                             enem_url=create_render_save_path(new_dir='enem', filename=course_name),
            )
            render_course_selection(jinja_env, result_dir,
                                    all_courses_dict=all_courses_dict)


# %%
render_courses(CONTENT_DIR, JINJA_ENV, ID_DF, GRADES_RESULT_DIR)


# %%
# # !rm -rf ../../website/notas/*

# %% [markdown]
# ### Essays

# %% [markdown]
# #### Lists

# %%
def join_essay_files(exam, essays_dir):
    essay_dir = join(essays_dir, exam)
    essay_filenames = listdir(essay_dir)
    essays_list = []
    for essay_filename in essay_filenames:
        essay_path = join(essay_dir, essay_filename)
        essays_list.append(pd.read_csv(essay_path).convert_dtypes())
    return pd.concat(essays_list, axis=0)


# %%
enem_essays = pd.read_csv(join(ESSAYS_DIR, 'enem.csv')).convert_dtypes()
enem_essays

# %%
fuvest_essays = pd.read_csv(join(ESSAYS_DIR, 'fuvest.csv')).convert_dtypes()
fuvest_essays


# %%
def build_years_dict(essays_df):
    years_dict = {}
    for year, essays in essays_df.groupby('ano'):
        essays_dict = {}
        for _, essay_series in essays.iterrows():
            essays_dict[essay_series['nota']] = essay_series.to_dict()
        years_dict[year] = essays_dict
    return years_dict


# %%
build_years_dict(enem_essays)


# %% [markdown]
# The cells below are commented out since they are only used for testing

# %%
# ESSAY_TEMPLATE = JINJA_ENV.get_template('redacoes.html.jinja')
# with open('enem.html', 'w') as f:
#     f.write(ESSAY_TEMPLATE.render(
#         years_dict=build_years_dict(enem_essays),
#         exam='Enem',
#         criteria=['c1', 'c2', 'c3', 'c4', 'c5'],
#         active_link='Redações',
#         root_path='../'))

# %%
# ESSAY_TEMPLATE = JINJA_ENV.get_template('redacoes.html.jinja')
# with open('fuvest.html', 'w') as f:
#     f.write(ESSAY_TEMPLATE.render(
#         years_dict=build_years_dict(fuvest_essays),
#         exam='Fuvest',
#         active_link='Redações',
#         root_path='../'))

# %% [markdown]
# #### Exam selection

# %%
# SELECTION_TEMPLATE = JINJA_ENV.get_template('vestibulares.html.jinja')
# selection_website = SELECTION_TEMPLATE.render(
#     active_link='Redações',
#     root_path='../',
#     render_fuvest=True,
#     render_enem=True,
#     fuvest_url='fuvest.html',
#     enem_url='enem.html',
#     button_text='Acesse as redações')
# save_website(selection_website, 'example_selection.html')

# %% [markdown]
# #### Final rendering

# %%
def render_essays(jinja_env, essays_dir, result_dir,
                  essay_template_filename='redacoes.html.jinja',
                  selection_template_filename='vestibulares.html.jinja'):
    for exam in ['enem', 'fuvest']:
        exam_essays = pd.read_csv(join(ESSAYS_DIR, exam + '.csv')).convert_dtypes()
        years_dict = build_years_dict(exam_essays)
        criteria = None
        if exam == 'enem':
            criteria = ['c1', 'c2', 'c3', 'c4', 'c5']

        essay_template = jinja_env.get_template(essay_template_filename)
        essay_website = essay_template.render(
            years_dict=years_dict,
            exam=exam,
            criteria=criteria,
            active_link='Redações',
            root_path='../')
        save_website(essay_website, join(result_dir, exam+'.html'))

    selection_template = jinja_env.get_template(selection_template_filename)
    selection_website = selection_template.render(
        active_link='Redações',
        root_path='../',
        render_fuvest=True,
        render_enem=True,
        fuvest_url='fuvest.html',
        enem_url='enem.html',
        button_text='Acesse as redações')
    save_website(selection_website, join(result_dir, 'vestibulares.html'))


# %%
render_essays(JINJA_ENV, ESSAYS_DIR, ESSAYS_RESULT_DIR)

# %%
# # !rm -rf ../../website/redacoes/*

# %%
