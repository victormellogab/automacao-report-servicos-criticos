import pandas as pd
import math

# Normalizar colunas de texto
def normalizar_texto(df, colunas):
    for col in colunas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df

# Calcular DiasDeExec (igual DAX)
def calcular_dias_exec(df, coluna_inicio, coluna_fim):
    df['DiasDeExec'] = (df[coluna_fim] - df[coluna_inicio]).dt.total_seconds() / (24 * 3600)
    df['DiasDeExec'] = df['DiasDeExec'].apply(lambda x: math.ceil(x))
    return df

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

# Criar StatusPrazo
def criar_status_prazo(df):
    df['StatusPrazo'] = df.apply(
        lambda x: 'No Prazo' if x['DiasDeExec'] <= x['PrazoPadrao'] else 'Fora do Prazo',
        axis=1
    )
    return df
