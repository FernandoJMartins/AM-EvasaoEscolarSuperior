# ...existing code...
import pandas as pd

file_path = './dados/MICRODADOS_CADASTRO_CURSOS_2024.csv'

# colunas que você quer
use_cols = ['NU_ANO_CENSO', 'NO_REGIAO', 'NO_UF']

# tenta ler somente essas colunas com alguns encodings comuns
for enc in ('cp1252', 'latin1', 'utf-8'):
    try:
        df_small = pd.read_csv(
            file_path,
            sep=';',
            encoding=enc,
            usecols=use_cols,
            dtype=str,
            on_bad_lines='warn',
            keep_default_na=False
        )
        print(f"Lido com encoding: {enc}")
        break
    except Exception as e:
        print(f"Falha ao ler com {enc}: {e}")
else:
    # fallback: ler tudo (mais lento) e então selecionar colunas
    df_all = pd.read_csv(file_path, sep=';', encoding='cp1252', dtype=str, on_bad_lines='skip', keep_default_na=False)
    df_small = df_all.reindex(columns=use_cols)

# mostrar resultado e salvar amostra
print("Shape:", df_small.shape)
print(df_small.head(50).to_string(index=False))

# salvar amostra para abrir no Excel se quiser
df_small.head(500).to_csv('./dados/sample_cols_nuanocenso_noregiao_nou_f.csv', index=False, sep=';')
print("Amostra salva em: ./dados/sample_cols_nuanocenso_noregiao_nou_f.csv")
# ...existing code...