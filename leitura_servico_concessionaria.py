### esse arquivo é um teste para ler a qtde de serviços geral, sem considerar alguma concessionária

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

# Mostrar os primeiros 20 valores como estão no CSV
print(df['Serv_Solicitado'].head(20).tolist())

# Mostrar os tipos de cada valor na coluna
print(df['Serv_Solicitado'].map(type).value_counts())

# --- Filtrar apenas o código de serviço 168 (numérico) ---
df_setembro_CAC_168 = df_setembro_CAC[df_setembro_CAC['Serv_Solicitado'] == 168]

# --- Excluir valores indesejados ---
df_filtrado = df_setembro_CAC_168[
    (df_setembro_CAC_168['AREA_EXEC'] != 'ENGENHARIA') &
    (df_setembro_CAC_168['Área Exec.'] != 'ENGENHARIA') &
    (df_setembro_CAC_168['DH_EXEC_INI_REL'].notna()) &
    (df_setembro_CAC_168['DH_EXEC_FIM_REL'].notna())
]

# --- Contar quantidade de serviços restantes (somando Nº O.S.) ---
quantidade_servicos = df_filtrado['Nº O.S.'].count()
print(f"Quantidade de serviços após filtros: {quantidade_servicos}")
