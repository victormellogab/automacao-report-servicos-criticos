import math
import pandas as pd

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

def gab_calcular_tempo_dax(row, df_os, df_servicos):
    serv = row['Servico_Limpo']

    # Seleciona tempos definidos para esse serviço
    tempos = df_servicos.loc[
        (df_servicos['Serviços'] == serv) &
        (df_servicos['Tempo Padrão'].notna()),
        'Tempo Padrão'
    ]

    # Caso NÃO exista tempo padrão para o serviço → BI retorna 0
    if tempos.empty:
        return 0

    # Remove tempos iguais a zero (BI ignora zeros na média)
    tempos_validos = tempos[tempos > 0]

    # Se só tinha zeros → retorna 0
    if tempos_validos.empty:
        return 0

    # Média das concessionárias que têm tempo > 0
    return round(tempos_validos.mean(), 2)
