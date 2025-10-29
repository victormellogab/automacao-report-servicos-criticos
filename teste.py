### esse código pega a qtde de OS de cac (inclusive da base) + a porcentagem de serviços no prazo e fora do prazo. arquivo teste

import pandas as pd
import os
import math

# --- Configurações de pastas e arquivos ---
caminho_inova = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Script Geração Report Serviços\Dados\CAC_SETEMBRO.csv"
caminho_servicos = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Script Geração Report Serviços\Dados\TODOS_SERVICOS.csv"
pasta_saida = r'H:\COMERCIAL\MEDIÇÃO\ARQUIVO MORTO\BERNARDO\GSC\Automação Report'
os.makedirs(pasta_saida, exist_ok=True)

# --- Ler CSVs ---
df = pd.read_csv(caminho_inova, sep=None, engine='python', encoding='latin1')
df_servicos = pd.read_csv(caminho_servicos, sep=None, engine='python', encoding='latin1')

# --- Limpar colunas de texto ---
colunas_texto_inova = ['EMPRESA', 'AREA_EXEC', 'Área Exec.', 'Servico_Limpo']
for col in colunas_texto_inova:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()

df_servicos['Serviços'] = df_servicos['Serviços'].astype(str).str.strip().str.upper()
df_servicos['Concessionária'] = df_servicos['Concessionária'].astype(str).str.strip().str.upper()

# --- Converter datas ---
df['DATA_HORA_INCL'] = pd.to_datetime(df['DATA_HORA_INCL'], dayfirst=True, errors='coerce')
df['DATA_BAIXA'] = pd.to_datetime(df['DATA_BAIXA'], dayfirst=True, errors='coerce')

# --- Remover registros inválidos ---
df = df[df['DATA_HORA_INCL'].notna() & df['DATA_BAIXA'].notna()]

# --- Filtrar mês e concessionária ---
data_inicio = pd.to_datetime('2025-09-01')
data_fim = pd.to_datetime('2025-09-30')
df = df[(df['DATA_BAIXA'] >= data_inicio) & (df['DATA_BAIXA'] <= data_fim)]
df = df[df['EMPRESA'] == 'CAC']

# --- Excluir registros de ENGENHARIA e sem datas de execução ---
df = df[(df['AREA_EXEC'] != 'ENGENHARIA') & (df['Área Exec.'] != 'ENGENHARIA')]
df = df[df['DH_EXEC_INI_REL'].notna() & df['DH_EXEC_FIM_REL'].notna()]

# --- Calcular DiasDeExec (igual DATEDIFF DAY do DAX) ---
df['DiasDeExec'] = (df['DATA_BAIXA'] - df['DATA_HORA_INCL']).dt.total_seconds() / (24*3600)
df['DiasDeExec'] = df['DiasDeExec'].apply(lambda x: math.ceil(x))  # arredondar para cima, como DAX

# --- Criar dicionário (Servico, Empresa) -> PrazoPadrao (como SELECTEDVALUE no DAX) ---
prazo_dict = df_servicos.drop_duplicates(subset=['Serviços','Concessionária']) \
    .set_index(['Serviços','Concessionária'])['Prazo para Empresa'].to_dict()

# --- Função para calcular PrazoPadrao fiel ao BI ---
def calcular_prazo_dax(row):
    serv = row['Servico_Limpo']
    empresa = row['EMPRESA']
    
    if (serv, empresa) in prazo_dict:
        return prazo_dict[(serv, empresa)]  # prazo específico da concessionária
    else:
        # média do serviço, ignorando concessionária (como DAX)
        prazos = df_servicos[df_servicos['Serviços'] == serv]['Prazo para Empresa']
        if not prazos.empty:
            return prazos.mean()
        else:
            return None

# --- Aplicar PrazoPadrao ---
df['PrazoPadrao'] = df.apply(calcular_prazo_dax, axis=1)

# --- Remover OS sem prazo definido (igual ao BI) ---
df = df[df['PrazoPadrao'].notna()]

# --- Criar StatusPrazo ---
df['StatusPrazo'] = df.apply(
    lambda x: 'No Prazo' if x['DiasDeExec'] <= x['PrazoPadrao'] else 'Fora do Prazo',
    axis=1
)

# --- Calcular % serviços no prazo e fora do prazo ---
total_os = len(df)
no_prazo = len(df[df['StatusPrazo'] == 'No Prazo'])
fora_prazo = len(df[df['StatusPrazo'] == 'Fora do Prazo'])

pct_no_prazo = round((no_prazo / total_os) * 100, 2) if total_os > 0 else 0
pct_fora_prazo = round((fora_prazo / total_os) * 100, 2) if total_os > 0 else 0

# --- Mostrar resultados ---
print(f"Total de OS: {total_os}")
print(f"No Prazo: {no_prazo} ({pct_no_prazo}%)")
print(f"Fora do Prazo: {fora_prazo} ({pct_fora_prazo}%)")
