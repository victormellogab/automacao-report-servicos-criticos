### esse arquivo é um teste para ler a qtde de serviços geral, considerando cac (inclusive na base)

import pandas as pd
import os

# --- Configurações de pasta e arquivo ---
caminho_arquivo = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Script Geração Report Serviços\Dados\CAC_SETEMBRO.csv"
pasta_saida = r'H:\COMERCIAL\MEDIÇÃO\ARQUIVO MORTO\BERNARDO\GSC\Automação Report'
os.makedirs(pasta_saida, exist_ok=True)

# --- Ler CSV exportado do BI ---
df = pd.read_csv(caminho_arquivo, sep=None, engine='python', encoding='latin1')

# --- Limpar colunas de texto para evitar espaços extras ou caracteres invisíveis ---
colunas_texto = ['EMPRESA', 'AREA_EXEC', 'Área Exec.']
for col in colunas_texto:
    df[col] = df[col].astype(str).str.strip().str.upper()

# Converter DATA_BAIXA para datetime, sem definir formato fixo
df['DATA_BAIXA'] = pd.to_datetime(df['DATA_BAIXA'], dayfirst=True, errors='coerce')

# Remover registros que não conseguiram ser convertidos
df = df[df['DATA_BAIXA'].notna()]

# --- Filtrar apenas setembro de 2025 ---
data_inicio = pd.to_datetime('2025-09-01 00:00:00')
data_fim = pd.to_datetime('2025-09-30 23:59:59')
df_setembro = df[(df['DATA_BAIXA'] >= data_inicio) & (df['DATA_BAIXA'] <= data_fim)]

# --- Filtrar apenas a concessionária CAC ---
df_setembro_CAC = df_setembro[df_setembro['EMPRESA'] == 'CAC']

# --- Excluir valores indesejados ---
df_filtrado = df_setembro_CAC[
    (df_setembro_CAC['AREA_EXEC'] != 'ENGENHARIA') &
    (df_setembro_CAC['Área Exec.'] != 'ENGENHARIA') &
    (df_setembro_CAC['DH_EXEC_INI_REL'].notna()) &
    (df_setembro_CAC['DH_EXEC_FIM_REL'].notna())
]

# --- Contar quantidade total de O.S. após filtros ---
quantidade_total_os = df_filtrado['Nº O.S.'].count()
print(f"Total de O.S. após filtros: {quantidade_total_os:,}".replace(",", "."))
