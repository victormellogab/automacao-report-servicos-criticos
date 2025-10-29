import pandas as pd
import os
import math

# Caminhos dos arquivos
caminho_inova = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Script Geração Report Serviços\Dados\data.xlsx"
caminho_servicos = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Script Geração Report Serviços\Dados\TODOS_SERVICOS.csv"

# Pasta de saída
pasta_saida = r'H:\COMERCIAL\MEDIÇÃO\ARQUIVO MORTO\BERNARDO\GSC\Automação Report'
os.makedirs(pasta_saida, exist_ok=True)

# Ler planilhas
df = pd.read_excel(caminho_inova, engine='openpyxl')
df_servicos = pd.read_csv(caminho_servicos, sep=None, engine='python', encoding='latin1')

# Normalizar colunas de texto
colunas_texto_inova = ['EMPRESA', 'AREA_EXEC', 'Área Exec.', 'Servico_Limpo']
for col in colunas_texto_inova:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()

df_servicos['Serviços'] = df_servicos['Serviços'].astype(str).str.strip().str.upper()
df_servicos['Concessionária'] = df_servicos['Concessionária'].astype(str).str.strip().str.upper()

# Converter datas
df['DATA_HORA_INCL'] = pd.to_datetime(df['DATA_HORA_INCL'], dayfirst=True, errors='coerce')
df['DATA_BAIXA'] = pd.to_datetime(df['DATA_BAIXA'], dayfirst=True, errors='coerce')

# Remover registros inválidos
df = df[df['DATA_HORA_INCL'].notna() & df['DATA_BAIXA'].notna()]

# Filtro de mês (setembro/2025)
data_inicio = pd.to_datetime('2025-09-01')
data_fim = pd.to_datetime('2025-09-30')
df = df[(df['DATA_BAIXA'] >= data_inicio) & (df['DATA_BAIXA'] <= data_fim)]

# Excluir registros de ENGENHARIA e sem datas de execução
df = df[(df['AREA_EXEC'] != 'ENGENHARIA') & (df['Área Exec.'] != 'ENGENHARIA')]
df = df[df['DH_EXEC_INI_REL'].notna() & df['DH_EXEC_FIM_REL'].notna()]

# Calcular DiasDeExec (como DATEDIFF DAY no DAX)
df['DiasDeExec'] = (df['DATA_BAIXA'] - df['DATA_HORA_INCL']).dt.total_seconds() / (24 * 3600)
df['DiasDeExec'] = df['DiasDeExec'].apply(lambda x: math.ceil(x))

# Dicionário (Serviço, Empresa) -> PrazoPadrao
prazo_dict = df_servicos.drop_duplicates(subset=['Serviços', 'Concessionária']) \
    .set_index(['Serviços', 'Concessionária'])['Prazo para Empresa'].to_dict()

# Função de cálculo do PrazoPadrao (fiel ao DAX)
def calcular_prazo_dax(row):
    serv = row['Servico_Limpo']
    empresa = row['EMPRESA']
    if (serv, empresa) in prazo_dict:
        return prazo_dict[(serv, empresa)]
    else:
        prazos = df_servicos[df_servicos['Serviços'] == serv]['Prazo para Empresa']
        if not prazos.empty:
            return prazos.mean()
        else:
            return None

# Aplicar PrazoPadrao
df['PrazoPadrao'] = df.apply(calcular_prazo_dax, axis=1)
df = df[df['PrazoPadrao'].notna()]

# Criar StatusPrazo
df['StatusPrazo'] = df.apply(
    lambda x: 'No Prazo' if x['DiasDeExec'] <= x['PrazoPadrao'] else 'Fora do Prazo',
    axis=1
)

# Listas das Concessionárias
concessionarias = [
    #'CAAN',
    #'CAC',
    #'CAI',
    #'CAIZ',
    #'CAJ',
    #'CAJA',
    #'CAN',
    #'CANF',
    #'CAP',
    #'CAPAM',
    'CAPY',
    #'CAV',
    #'RIOMAIS'
]

# Loop por concessionária
for conc in concessionarias:
    df_conc = df[df['EMPRESA'] == conc]

    total_os = len(df_conc)
    no_prazo = len(df_conc[df_conc['StatusPrazo'] == 'No Prazo'])
    fora_prazo = len(df_conc[df_conc['StatusPrazo'] == 'Fora do Prazo'])

    pct_no_prazo = round((no_prazo / total_os) * 100, 2) if total_os > 0 else 0
    pct_fora_prazo = round((fora_prazo / total_os) * 100, 2) if total_os > 0 else 0

    print(f"\n--- {conc} ---")
    print(f"Total de OS: {total_os}")
    print(f"No Prazo: {no_prazo} ({pct_no_prazo}%)")
    print(f"Fora do Prazo: {fora_prazo} ({pct_fora_prazo}%)")
