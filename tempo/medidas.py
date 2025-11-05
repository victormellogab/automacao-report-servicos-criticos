import math

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
