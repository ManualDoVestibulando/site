import os
import pandas as pd

def merge_nan_cols(df, col_regex):
    selected_col_df = df.filter(regex=col_regex)
    merged_col_series = selected_col_df.apply((
        lambda x:
            x.dropna()[-1]),
        axis=1)
    return merged_col_series

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

if __name__ == '__main__':
    FORM_DIR = 'data/1_raw/forms'
    RESULT_DIR = 'data/2_intermediate/forms'

    enem_list = []
    fuvest_list = []

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

        fuvest_list.append(fuvest)
        enem_list.append(enem)

    fuvest_concat = pd.concat(fuvest_list, axis=0)
    enem_concat = pd.concat(enem_list, axis=0)

    fuvest_concat.convert_dtypes().to_csv(os.path.join(RESULT_DIR, 'fuvest.csv'), index=None)
    enem_concat.convert_dtypes().to_csv(os.path.join(RESULT_DIR, 'enem.csv'), index=None)
