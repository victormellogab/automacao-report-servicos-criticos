import math
import pandas as pd

# Calcular DiasDeExec
def calcular_dias_exec(df, coluna_inicio, coluna_fim):
    df['DiasDeExec'] = (df[coluna_fim] - df[coluna_inicio]).dt.total_seconds() / (24 * 3600)
    df['DiasDeExec'] = df['DiasDeExec'].apply(lambda x: math.ceil(x))
    return df

# Criar StatusPrazo
def criar_status_prazo(df):
    # Ajuste de prazo conforme regra
    df['PrazoAjustado'] = df.apply(
        lambda x: x['Prazo da Empresa'] + pd.Timedelta(days=3)
        if x['Área Exec.'] == 'GESTÃO DE SERVIÇOS - COMERCIAL'
        else x['Prazo da Empresa'],
        axis=1
    )

    # Criar StatusPrazo seguindo o SWITCH do DAX
    def status(row):
        if pd.isna(row['DATA_BAIXA']):
            return "Em Andamento"
        elif row['DATA_BAIXA'] <= row['PrazoAjustado']:
            return "No Prazo"
        else:
            return "Fora do Prazo"

    df['StatusPrazo'] = df.apply(status, axis=1)

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
