import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

file_path = './dados/MICRODADOS_CADASTRO_CURSOS_2024.csv'

# Colunas ajustadas para o problema de EVASÃO
# Inclui TRANCADA e FALECIDO para uma definição mais completa da evasão
use_cols = ['QT_SIT_TRANCADA', 'QT_SIT_DESVINCULADO', 'QT_SIT_TRANSFERIDO', 'QT_SIT_FALECIDO', 'QT_MAT', 'QT_CONC', 'QT_ING']

# --- [ SEÇÃO ORIGINAL: Leitura do Arquivo ] ---
# Tenta ler somente essas colunas com alguns encodings comuns
for enc in ('cp1252', 'latin1', 'utf-8'):
    try:
        # A lógica de leitura é mantida, garantindo que usecols e sep=';' sejam aplicados
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
    # Se todas as tentativas falharem (fallback), carregue o arquivo completo (lento)
    print("Tentativas de leitura falharam. Usando fallback...")
    df_all = pd.read_csv(file_path, sep=';', encoding='cp1252', dtype=str, on_bad_lines='skip', keep_default_na=False)
    df_small = df_all.reindex(columns=use_cols)

print("Shape inicial após a leitura:", df_small.shape)

# =========================================================================
# --- [ SEÇÃO ADICIONADA: TRATAMENTO DE DADOS (Passos 1 a 5) ] ---
# =========================================================================

# PASSO 1: CONVERSÃO DE TIPOS E TRATAMENTO DE NULOS
print("\n[PASSO 1 & 3]: Conversão para Numérico e Tratamento de Nulos...")

# Colunas que DEVEM ser numéricas
cols_numeric = use_cols
df_tratado = df_small.copy()

for col in cols_numeric:
    # Converte strings para números (valores não-numéricos viram NaN)
    df_tratado[col] = pd.to_numeric(df_tratado[col], errors='coerce')

# Tratamento de Nulos: Em colunas de contagem, NaN é substituído por 0.
df_tratado = df_tratado.fillna(0)

# PASSO 2: CRIAÇÃO DA VARIÁVEL ALVO (TARGET) - EVASAO
print("[PASSO 2]: Criação da Variável Alvo 'EVASAO'...")

# DEFINIÇÃO DA EVASÃO: O curso é considerado com evasão se houver alunos desvinculados,
# transferidos, trancados ou falecidos (indicando que não concluíram o ciclo).
df_tratado['EVASAO'] = (
    (df_tratado['QT_SIT_DESVINCULADO'] > 0) |
    (df_tratado['QT_SIT_TRANSFERIDO'] > 0) |
    (df_tratado['QT_SIT_TRANCADA'] > 0) |
    (df_tratado['QT_SIT_FALECIDO'] > 0)
).astype(int)

# PASSO 4: FEATURE ENGINEERING E ESCALONAMENTO
print("[PASSO 4]: Feature Engineering (Taxa de Evasão) e Escalonamento...")

# Criação da Taxa de Evasão: (Evasão + Trancados) / Matriculados
# Usa np.where para evitar divisão por zero (substitui QT_MAT=0 por 1 no denominador)
df_tratado['QT_MAT_SAFE'] = np.where(df_tratado['QT_MAT'] == 0, 1, df_tratado['QT_MAT'])
df_tratado['TAXA_EVASAO'] = (
    df_tratado['QT_SIT_DESVINCULADO'] +
    df_tratado['QT_SIT_TRANSFERIDO'] +
    df_tratado['QT_SIT_TRANCADA']
) / df_tratado['QT_MAT_SAFE']
df_tratado = df_tratado.drop(columns=['QT_MAT_SAFE']) # Remove a coluna de segurança

# Opcional: Escalonamento das Features
# scaler = StandardScaler()
# features_to_scale = ['QT_MAT', 'QT_CONC', 'QT_ING', 'TAXA_EVASAO']
# df_tratado[features_to_scale] = scaler.fit_transform(df_tratado[features_to_scale])
# print("Variáveis escalonadas com StandardScaler.")


# PASSO 5: PREVENÇÃO DE DATA LEAKAGE (Remoção das Colunas-Fonte)
print("[PASSO 5]: Prevenção de Data Leakage...")

# Remove as colunas que foram usadas para criar 'EVASAO'
cols_to_drop = [
    'QT_SIT_DESVINCULADO',
    'QT_SIT_TRANSFERIDO',
    'QT_SIT_TRANCADA',
    'QT_SIT_FALECIDO' # O falecimento é mantido para a definição da evasão, mas removido das features
]

df_final = df_tratado.drop(columns=cols_to_drop)


# --- [ SEÇÃO ORIGINAL: Mostrar e Salvar Resultados (Modificada) ] ---

# Mostrar resultado do dataset final
print("\nShape FINAL (Pronto para o Modelo):", df_final.shape)
print("\nDataset Final (Features + Target):")
print(df_final.head(10).to_string(index=False))

# Salvar amostra do dataset final para conferência
df_final.head(500).to_csv('./dados/sample_cols_tratado_final.csv', index=False, sep=';')
print("\nAmostra FINAL salva em: ./dados/sample_cols_tratado_final.csv")