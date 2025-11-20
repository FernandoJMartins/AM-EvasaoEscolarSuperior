import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

file_path = './dados/MICRODADOS_CADASTRO_CURSOS_2024.CSV'

cols_numericas = [
    'QT_SIT_TRANCADA', 'QT_SIT_DESVINCULADO', 'QT_SIT_TRANSFERIDO',
    'QT_SIT_FALECIDO', 'QT_MAT', 'QT_CONC', 'QT_ING'
]

cols_categoricas = [
    'NO_CURSO',
    'NO_MUNICIPIO',
    'SG_UF',
    'TP_MODALIDADE_ENSINO',   
    'TP_GRAU_ACADEMICO',      
    'IN_GRATUITO'             
]

use_cols = cols_numericas + cols_categoricas



df_test = pd.read_csv(file_path, sep=';', encoding='cp1252', nrows=10)
df_test.columns = df_test.columns.str.strip()

print("\n➡ COLUNAS ENCONTRADAS NO CSV:")
print(df_test.columns.tolist())

# Mapear colunas reais
col_map = {}
for col in use_cols:
    if col in df_test.columns:
        col_map[col] = col
    else:
        possivel = [
            c for c in df_test.columns
            if col.replace("_", "").lower() in c.replace("_", "").lower()
        ]
        if possivel:
            col_map[col] = possivel[0]
            print(f"⚠ MAPEADO '{col}' → '{possivel[0]}'")
        else:
            col_map[col] = None
            print(f"❌ NÃO ENCONTRADO NO CSV: {col}")

cols_validas = [v for v in col_map.values() if v is not None]

print("\n➡ COLUNAS QUE SERÃO LIDAS:")
print(cols_validas)


df = pd.read_csv(
    file_path,
    sep=';',
    encoding='cp1252',
    usecols=cols_validas,
    dtype=str,
    keep_default_na=False,
    on_bad_lines='warn'
)

df.columns = df.columns.str.strip()



if col_map["SG_UF"] is not None:
    col_real = col_map["SG_UF"]
    print(f"\n➡ Filtrando registros onde {col_real} == 'PB' ...")
    print("Shape antes do filtro:", df.shape)
    df = df[df[col_real] == "PB"]
    print("Shape após filtro PB:", df.shape)
else:
    print("\n⚠ Não foi possível filtrar por SG_UF (coluna não encontrada).")

df_tratado = df.copy()



print("\nConversão Numérica e Nulos...")

for col in cols_numericas:
    if col_map[col] is not None:
        df_tratado[col] = pd.to_numeric(df_tratado[col_map[col]], errors='coerce')
    else:
        df_tratado[col] = 0

df_tratado[cols_numericas] = df_tratado[cols_numericas].fillna(0)



print("Criando variável alvo 'EVASAO'...")

df_tratado['EVASAO'] = (
    (df_tratado['QT_SIT_DESVINCULADO'] > 0) |
    (df_tratado['QT_SIT_TRANSFERIDO'] > 0) |
    (df_tratado['QT_SIT_TRANCADA'] > 0) |
    (df_tratado['QT_SIT_FALECIDO'] > 0)
).astype(int)



print("Extraindo dados Brutos")

df_tratado['QT_MAT_SAFE'] = np.where(df_tratado['QT_MAT'] == 0, 1, df_tratado['QT_MAT'])

df_tratado['TAXA_EVASAO'] = (
    df_tratado['QT_SIT_DESVINCULADO'] +
    df_tratado['QT_SIT_TRANSFERIDO'] +
    df_tratado['QT_SIT_TRANCADA']
) / df_tratado['QT_MAT_SAFE']

df_tratado = df_tratado.drop(columns=['QT_MAT_SAFE'])



print("Removendo colunas de evasao individuais...")

cols_to_drop = [
    'QT_SIT_DESVINCULADO',
    'QT_SIT_TRANSFERIDO',
    'QT_SIT_TRANCADA',
    'QT_SIT_FALECIDO'
]

df_final = df_tratado.drop(columns=cols_to_drop)


def traduz_modalidade(x):
    return {
        "1": "Presencial",
        "2": "EaD"
    }.get(str(x), "Desconhecido")

def traduz_grau(x):
    return {
        "1": "Bacharelado",
        "2": "Licenciatura",
        "3": "Tecnológico"
    }.get(str(x), "Desconhecido")

df_final['MODALIDADE'] = df_final[col_map['TP_MODALIDADE_ENSINO']].apply(traduz_modalidade)
df_final['GRAU'] = df_final[col_map['TP_GRAU_ACADEMICO']].apply(traduz_grau)
df_final['GRATUITO'] = df_final[col_map['IN_GRATUITO']].map({'1': 'Sim', '0': 'Não'})



print("\nShape FINAL:", df_final.shape)
print("\nPRIMEIRAS 50 LINHAS:")
print(df_final.head(150).to_string(index=False))

df_final.head(500).to_csv('./dados/sample_cols_tratado_final.csv', index=False, sep=';')
print("\nAmostra salva em: ./dados/sample_cols_tratado_final.csv")
