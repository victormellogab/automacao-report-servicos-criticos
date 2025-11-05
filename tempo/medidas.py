import math
import pandas as pd

# Calcular DiasDeExec
def calcular_dias_exec(df, coluna_inicio, coluna_fim):
    df['DiasDeExec'] = (df[coluna_fim] - df[coluna_inicio]).dt.total_seconds() / (24 * 3600)
    df['DiasDeExec'] = df['DiasDeExec'].apply(lambda x: math.ceil(x))
    return df

# Criar StatusPrazo
def criar_status_prazo(df):
    df['StatusPrazo'] = df.apply(
        lambda x: 'No Prazo' if x['DiasDeExec'] <= x['PrazoPadrao'] else 'Fora do Prazo',
        axis=1
    )
    return df

# Criar dicionário de PrazoPadrao
def criar_prazo_dict(df_servicos):
    return df_servicos.drop_duplicates(subset=['Serviços', 'Concessionária']) \
        .set_index(['Serviços', 'Concessionária'])['Prazo para Empresa'].to_dict()

# Calcular PrazoPadrao baseado em dicionário
def calcular_prazo_dax(row, prazo_dict, df_servicos):
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

# -------------------------------------------------

def calcular_tempo_padrao_dinamico(df, df_servicos):
    # Padroniza nomes para evitar conflito
    servicos = df_servicos.rename(columns={
        'Serviços': 'Servico_Limpo',
        'Concessionária': 'EMPRESA',
        'Tempo Padrão': 'TempoPadrao'
    })

    # 1) Faz merge para pegar Tempo Padrão específico da concessionária
    df = df.merge(servicos[['Servico_Limpo', 'EMPRESA', 'TempoPadrao']], 
                  on=['Servico_Limpo', 'EMPRESA'], how='left')

    # 2) Cria média geral por serviço (caso a concessionária não tenha tempo definido)
    media_geral = servicos.groupby('Servico_Limpo')['TempoPadrao'].mean().to_dict()

    # 3) Preenche onde TempoPadrao ficou NaN com a média geral
    df['TempoPadrao'] = df.apply(
        lambda x: media_geral.get(x['Servico_Limpo']) if pd.isna(x['TempoPadrao']) else x['TempoPadrao'],
        axis=1
    )

    return df
