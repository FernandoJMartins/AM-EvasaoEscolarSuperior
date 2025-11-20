import pandas as pd
import numpy as np
import os

sample_file = './dados/sample_cols_tratado_final.csv'
orig_file = './dados/MICRODADOS_CADASTRO_CURSOS_2024.CSV'

def load_data():
    if os.path.exists(sample_file):
        df = pd.read_csv(sample_file, sep=';', encoding='cp1252', dtype=str)
        # garantir tipos numéricos para colunas esperadas
        for c in ['EVASAO','QT_SIT_TRANCADA','QT_SIT_DESVINCULADO','QT_SIT_TRANSFERIDO','QT_SIT_FALECIDO','QT_MAT']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
    else:
        df = pd.read_csv(orig_file, sep=';', encoding='cp1252', dtype=str, on_bad_lines='warn')
        df.columns = df.columns.str.strip()
        numcols = ['QT_SIT_TRANCADA','QT_SIT_DESVINCULADO','QT_SIT_TRANSFERIDO','QT_SIT_FALECIDO','QT_MAT']
        for c in numcols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            else:
                df[c] = 0
        df['EVASAO'] = ((df['QT_SIT_DESVINCULADO']>0)|(df['QT_SIT_TRANSFERIDO']>0)|(df['QT_SIT_TRANCADA']>0)|(df['QT_SIT_FALECIDO']>0)).astype(int)
        if 'TP_MODALIDADE_ENSINO' in df.columns:
            df['MODALIDADE'] = df['TP_MODALIDADE_ENSINO'].astype(str).map({'1':'Presencial','2':'EaD'}).fillna('Desconhecido')
        else:
            df['MODALIDADE'] = 'Desconhecido'
        if 'IN_GRATUITO' in df.columns:
            df['GRATUITO'] = df['IN_GRATUITO'].astype(str).map({'1':'Sim','0':'Não'}).fillna('Não')
        else:
            df['GRATUITO'] = 'Não'
        if 'TP_GRAU_ACADEMICO' in df.columns:
            df['GRAU'] = df['TP_GRAU_ACADEMICO'].astype(str).map({'1':'Bacharelado','2':'Licenciatura','3':'Tecnológico'}).fillna('Desconhecido')
        else:
            df['GRAU'] = 'Desconhecido'
    return df

def summary_stats(df):
    df = df.copy()
    if df['EVASAO'].dtype == object:
        df['EVASAO'] = pd.to_numeric(df['EVASAO'], errors='coerce').fillna(0).astype(int)
    total = int(df.shape[0])
    ev_count = int(df['EVASAO'].sum())
    ev_mean = float(df['EVASAO'].mean())
    ev_median = float(df['EVASAO'].median())
    ev_std = float(df['EVASAO'].std(ddof=0)) if total>1 else 0.0
    ev_min = int(df['EVASAO'].min())
    ev_max = int(df['EVASAO'].max())
    ev_pct = ev_mean * 100.0
    return {
        'count': total,
        'evasao_count': ev_count,
        'evasao_mean': ev_mean,
        'evasao_median': ev_median,
        'evasao_std': ev_std,
        'evasao_min': ev_min,
        'evasao_max': ev_max,
        'evasao_pct': ev_pct
    }

def percent_by_municipio(df, top_n=50):
    if 'NO_MUNICIPIO' not in df.columns:
        return pd.DataFrame(columns=['NO_MUNICIPIO','count','evasao_count','evasao_rate'])
    # garantir EVASAO numérico antes da agregação
    df = df.copy()
    if 'EVASAO' in df.columns:
        df['EVASAO'] = pd.to_numeric(df['EVASAO'], errors='coerce').fillna(0).astype(int)
    g = df.groupby('NO_MUNICIPIO')['EVASAO'].agg(['count','sum'])
    g = g.rename(columns={'sum':'evasao_count'})
    # garantir tipos numéricos antes da divisão
    g['count'] = pd.to_numeric(g['count'], errors='coerce').fillna(0)
    g['evasao_count'] = pd.to_numeric(g['evasao_count'], errors='coerce').fillna(0)
    g['evasao_rate'] = (g['evasao_count'] / g['count']) * 100.0
    g = g.sort_values('evasao_rate', ascending=False)
    return g.reset_index().head(top_n)

def percent_by_category(df, cat_col):
    if cat_col not in df.columns:
        return pd.DataFrame(columns=[cat_col,'count','evasao_count','evasao_rate'])
    df = df.copy()
    if 'EVASAO' in df.columns:
        df['EVASAO'] = pd.to_numeric(df['EVASAO'], errors='coerce').fillna(0).astype(int)
    g = df.groupby(cat_col)['EVASAO'].agg(['count','sum'])
    g = g.rename(columns={'sum':'evasao_count'})
    g['count'] = pd.to_numeric(g['count'], errors='coerce').fillna(0)
    g['evasao_count'] = pd.to_numeric(g['evasao_count'], errors='coerce').fillna(0)
    g['evasao_rate'] = (g['evasao_count'] / g['count']) * 100.0
    g = g.sort_values('evasao_rate', ascending=False)
    return g.reset_index()

def main():
    df = load_data()
    stats = summary_stats(df)
    print('ESTATÍSTICAS GERAIS')
    for k,v in stats.items():
        print(f"{k}: {v}")
    municipio = percent_by_municipio(df, top_n=200)
    modalidade = percent_by_category(df, 'MODALIDADE')
    gratuito = percent_by_category(df, 'GRATUITO')
    grau = percent_by_category(df, 'GRAU')
    out_summary = pd.DataFrame([stats])
    out_summary.to_csv('./dados/summary_evasao.csv', index=False, sep=';')
    municipio.to_csv('./dados/percentual_por_municipio.csv', index=False, sep=';')
    modalidade.to_csv('./dados/percentual_por_modalidade.csv', index=False, sep=';')
    gratuito.to_csv('./dados/percentual_por_gratuito.csv', index=False, sep=';')
    grau.to_csv('./dados/percentual_por_grau.csv', index=False, sep=';')
    print('\nArquivos gerados:')
    print('./dados/summary_evasao.csv')
    print('./dados/percentual_por_municipio.csv')
    print('./dados/percentual_por_modalidade.csv')
    print('./dados/percentual_por_gratuito.csv')
    print('./dados/percentual_por_grau.csv')

if __name__ == '__main__':
    main()