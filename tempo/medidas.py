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
