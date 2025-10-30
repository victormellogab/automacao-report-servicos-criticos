import pandas as pd
import os
import math
import matplotlib.pyplot as plt

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

# --- Filtro para setembro/2025 (top 10 atual) ---
data_inicio = pd.to_datetime('2025-09-01')
data_fim = pd.to_datetime('2025-09-30')
df_setembro = df[(df['DATA_BAIXA'] >= data_inicio) & (df['DATA_BAIXA'] <= data_fim)]

# Excluir registros de ENGENHARIA e sem datas de execução
df_setembro = df_setembro[(df_setembro['AREA_EXEC'] != 'ENGENHARIA') & (df_setembro['Área Exec.'] != 'ENGENHARIA')]
df_setembro = df_setembro[df_setembro['DH_EXEC_INI_REL'].notna() & df_setembro['DH_EXEC_FIM_REL'].notna()]

# Calcular DiasDeExec (como DATEDIFF DAY no DAX)
df_setembro['DiasDeExec'] = (df_setembro['DATA_BAIXA'] - df_setembro['DATA_HORA_INCL']).dt.total_seconds() / (24 * 3600)
df_setembro['DiasDeExec'] = df_setembro['DiasDeExec'].apply(lambda x: math.ceil(x))

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
df_setembro['PrazoPadrao'] = df_setembro.apply(calcular_prazo_dax, axis=1)
df_setembro = df_setembro[df_setembro['PrazoPadrao'].notna()]

# Criar StatusPrazo
df_setembro['StatusPrazo'] = df_setembro.apply(
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

# --- Loop por concessionária para top 10 do mês (igual código atual) ---
for conc in concessionarias:
    df_conc = df_setembro[df_setembro['EMPRESA'] == conc]

    total_os = len(df_conc)
    no_prazo = len(df_conc[df_conc['StatusPrazo'] == 'No Prazo'])
    fora_prazo = len(df_conc[df_conc['StatusPrazo'] == 'Fora do Prazo'])

    pct_no_prazo = round((no_prazo / total_os) * 100, 2) if total_os > 0 else 0
    pct_fora_prazo = round((fora_prazo / total_os) * 100, 2) if total_os > 0 else 0

    print(f"\n--- {conc} ---")
    print(f"Total de OS: {total_os}")
    print(f"No Prazo: {no_prazo} ({pct_no_prazo}%)")
    print(f"Fora do Prazo: {fora_prazo} ({pct_fora_prazo}%)")

    # --- Tabela Top 10 piores serviços ---
    resumo = df_conc.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        Diferença=('DiasDeExec', lambda x: x.mean() - df_conc.loc[x.index, 'PrazoPadrao'].mean()),
        No_Prazo=('StatusPrazo', lambda x: (x=='No Prazo').sum())
    ).reset_index()

    resumo['%_No_Prazo'] = round((resumo['No_Prazo'] / resumo['Qtde_OS']) * 100, 2)

    top10 = resumo.sort_values('%_No_Prazo').head(10)
    top10 = top10[['Servico_Limpo','Qtde_OS','Prazo_Padrao','Media_Execucao','Diferença','%_No_Prazo']]

    print("\nTop 10 piores serviços (% no prazo mais baixo):")
    print(top10.to_string(index=False))


# --- NOVO: Top 3 últimos 3 meses ---
# Filtrar últimos 3 meses (julho a setembro/2025)
data_inicio_3mes = pd.to_datetime('2025-07-01')
data_fim_3mes = pd.to_datetime('2025-09-30')
df_3meses = df[(df['DATA_BAIXA'] >= data_inicio_3mes) & (df['DATA_BAIXA'] <= data_fim_3mes)]

# Excluir registros de ENGENHARIA e sem datas de execução
df_3meses = df_3meses[(df_3meses['AREA_EXEC'] != 'ENGENHARIA') & (df_3meses['Área Exec.'] != 'ENGENHARIA')]
df_3meses = df_3meses[df_3meses['DH_EXEC_INI_REL'].notna() & df_3meses['DH_EXEC_FIM_REL'].notna()]

# Calcular DiasDeExec
df_3meses['DiasDeExec'] = (df_3meses['DATA_BAIXA'] - df_3meses['DATA_HORA_INCL']).dt.total_seconds() / (24 * 3600)
df_3meses['DiasDeExec'] = df_3meses['DiasDeExec'].apply(lambda x: math.ceil(x))

# Aplicar PrazoPadrao e StatusPrazo
df_3meses['PrazoPadrao'] = df_3meses.apply(calcular_prazo_dax, axis=1)
df_3meses = df_3meses[df_3meses['PrazoPadrao'].notna()]
df_3meses['StatusPrazo'] = df_3meses.apply(
    lambda x: 'No Prazo' if x['DiasDeExec'] <= x['PrazoPadrao'] else 'Fora do Prazo',
    axis=1
)

# Loop por concessionária para top 3 últimos 3 meses
for conc in concessionarias:
    df_conc_3mes = df_3meses[df_3meses['EMPRESA'] == conc]

    resumo_3mes = df_conc_3mes.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        Diferença=('DiasDeExec', lambda x: x.mean() - df_conc_3mes.loc[x.index, 'PrazoPadrao'].mean()),
        No_Prazo=('StatusPrazo', lambda x: (x=='No Prazo').sum())
    ).reset_index()

    # Filtrar serviços com 10 ou mais OS
    resumo_3mes = resumo_3mes[resumo_3mes['Qtde_OS'] >= 10]

    resumo_3mes['%_No_Prazo'] = round((resumo_3mes['No_Prazo'] / resumo_3mes['Qtde_OS']) * 100, 2)

    top3_3mes = resumo_3mes.sort_values('%_No_Prazo').head(3)
    top3_3mes = top3_3mes[['Servico_Limpo','Qtde_OS','Prazo_Padrao','Media_Execucao','Diferença','%_No_Prazo']]

    print(f"\nTop 3 piores serviços últimos 3 meses ({conc}) - apenas serviços com >=10 OS:")
    print(top3_3mes.to_string(index=False))

# Loop por concessionária
for conc in concessionarias:

    df_conc = df[(df['EMPRESA'] == conc) &
                 (df['DATA_BAIXA'] >= pd.to_datetime('2025-04-01')) &
                 (df['DATA_BAIXA'] <= pd.to_datetime('2025-09-30'))]

    # Excluir ENGENHARIA e só considerar serviços com tempo de execução
    df_conc = df_conc[(df_conc['AREA_EXEC'] != 'ENGENHARIA') & (df_conc['Área Exec.'] != 'ENGENHARIA')]
    df_conc = df_conc[df_conc['DH_EXEC_INI_REL'].notna() & df_conc['DH_EXEC_FIM_REL'].notna()]

    # Calcular DiasDeExec
    df_conc['DiasDeExec'] = (df_conc['DATA_BAIXA'] - df_conc['DATA_HORA_INCL']).dt.total_seconds() / (24 * 3600)
    df_conc['DiasDeExec'] = df_conc['DiasDeExec'].apply(lambda x: math.ceil(x))

    # Aplicar PrazoPadrao e StatusPrazo
    df_conc['PrazoPadrao'] = df_conc.apply(calcular_prazo_dax, axis=1)
    df_conc = df_conc[df_conc['PrazoPadrao'].notna()]

    df_conc['StatusPrazo'] = df_conc.apply(
        lambda x: 'No Prazo' if x['DiasDeExec'] <= x['PrazoPadrao'] else 'Fora do Prazo',
        axis=1
    )

    # Criar coluna de mês
    df_conc['Mes'] = df_conc['DATA_BAIXA'].dt.to_period('M').dt.to_timestamp()

    # Agrupar por mês
    resumo_conc = df_conc.groupby('Mes').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
    ).reset_index()

    resumo_conc['%_No_Prazo'] = round((resumo_conc['No_Prazo'] / resumo_conc['Qtde_OS']) * 100, 2)

    # Ordenar por mês
    resumo_conc = resumo_conc.sort_values('Mes')

    # Preparar dados para gráfico
    meses = resumo_conc['Mes'].dt.strftime('%b/%Y')
    qtde_os = resumo_conc['Qtde_OS']
    pct_no_prazo = resumo_conc['%_No_Prazo']

    # --- Criar gráfico ---
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Barras = quantidade de OS
    bars = ax1.bar(meses, qtde_os, label='Quantidade de OS', color='skyblue')
    ax1.set_xlabel('Mês')
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_yticks([])  # remove ticks do eixo Y

    # Adicionar os valores acima das barras
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 3,
                 f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Linha = % no prazo
    ax2 = ax1.twinx()
    ax2.plot(meses, pct_no_prazo, marker='o', color='orange', linewidth=2, label='% No Prazo')
    ax2.set_yticks([])  # remove ticks do eixo Y

    # Adicionar valores da linha (% no prazo) acima dos pontos
    for i, pct in enumerate(pct_no_prazo):
        ax2.text(i, pct + 1.5, f'{pct}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='orange')

    # Título
    plt.title(f'{conc} — Evolução Mensal (Abr → Set 2025)\nQtde de Serviços x % No Prazo')

    fig.tight_layout()

    # Salvar gráfico
    caminho_grafico = os.path.join(pasta_saida, f'{conc}_Evolucao_Abr-Set_2025.png')
    plt.savefig(caminho_grafico, dpi=300)
    plt.close()

    print(f"\n✅ Gráfico {conc} salvo em: {caminho_grafico}")
