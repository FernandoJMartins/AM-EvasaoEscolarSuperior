# ...existing code...
import csv
import pandas as pd

file_path = './dados/MICRODADOS_CADASTRO_CURSOS_2024.csv'

for enc in ('utf-8', 'cp1252', 'latin1', 'iso-8859-1'):
    try:
        # primeiro tenta autodetectar delimitador com csv.Sniffer
        with open(file_path, 'r', encoding=enc, errors='replace') as f:
            sample = f.read(20000)
        try:
            delim = csv.Sniffer().sniff(sample).delimiter
        except Exception:
            delim = None  # deixa pandas tentar (sep=None) ou usar padrão ','
        if delim:
            # quando sabemos o separador usamos engine 'c' e podemos passar low_memory
            df = pd.read_csv(
                file_path,
                encoding=enc,
                sep=delim,
                engine='c',
                low_memory=False  # suportado pelo engine 'c'
            )
            print(f"Arquivo carregado com encoding: {enc} e separador: {delim} (engine=c)")
        else:
            # sep=None + engine='python' ativa detecção automática de delimitador
            # não passar low_memory porque o engine='python' não suporta essa opção
            df = pd.read_csv(
                file_path,
                encoding=enc,
                sep=None,
                engine='python',
                on_bad_lines='warn'  # pular/avisar linhas malformadas
            )
            print(f"Arquivo carregado com encoding: {enc} e separador: auto (engine=python)")
        break
    except UnicodeDecodeError:
        continue
    except pd.errors.ParserError as e:
        print(f"ParserError com encoding {enc}: {e}")
        continue
else:
    # último recurso: forçar leitura substituindo caracteres inválidos e pular linhas ruins
    df = pd.read_csv(
        file_path,
        encoding='utf-8',
        errors='replace',
        sep=None,
        engine='python',
        on_bad_lines='skip'  # pular linhas problemáticas
    )
    print("Arquivo carregado com errors='replace' e on_bad_lines='skip'")

# ...existing code...
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nPrimeiras 10 linhas:")
print(df.head(10).to_string(index=False))

# mostrar primeiras linhas brutas do arquivo (útil para checar delimitador/aspas)
print("\n--- Primeiras 20 linhas brutas do arquivo ---")
with open(file_path, 'r', encoding=enc_used, errors='replace') as f:
    for i, line in enumerate(f):
        if i >= 20:
            break
        print(f"{i+1:02d}: {line.rstrip()}")