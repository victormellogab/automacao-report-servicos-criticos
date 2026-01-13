import pandas as pd

def gerar_top3_concessionarias(df):
    if df.empty:
        return pd.DataFrame(columns=[
            'Servico_Limpo',
            'Qtde_OS',
            'TempoPadrao',
            'Media_Execucao',
            'Diferenca',
            '%_No_Tempo'
        ])

    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('TEMPO_EXEC_MIN', 'mean'),
        No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
    ).reset_index()

    # ✅ Blindagem de tipos
    resumo[['Qtde_OS', 'No_Tempo']] = resumo[['Qtde_OS', 'No_Tempo']].apply(
        pd.to_numeric, errors='coerce'
    ).fillna(0)

    resumo = resumo[resumo['Qtde_OS'] > 0]

    resumo[['TempoPadrao', 'Media_Execucao']] = resumo[
        ['TempoPadrao', 'Media_Execucao']
    ].apply(pd.to_numeric, errors='coerce')

    resumo['Diferenca'] = resumo['Media_Execucao'] - resumo['TempoPadrao']

    resumo['%_No_Tempo'] = (
        resumo['No_Tempo'] / resumo['Qtde_OS'] * 100
    ).round(2)

    # ✅ Regra de corte depois de tudo tratado
    resumo = resumo[resumo['Qtde_OS'] >= 10]

    top3 = resumo.sort_values('%_No_Tempo').head(3)

    return top3[
        [
            'Servico_Limpo',
            'Qtde_OS',
            'TempoPadrao',
            'Media_Execucao',
            'Diferenca',
            '%_No_Tempo'
        ]
    ]

def gerar_top3(df):
    # Agrupamento inicial por serviço
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('TEMPO_EXEC_MIN', 'mean'),
        No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
    ).reset_index()

    # Diferença
    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['TempoPadrao']

    # % no tempo
    resumo['%_No_Tempo'] = round(
        (resumo['No_Tempo'] / resumo['Qtde_OS']) * 100, 2
    )

    # === 🔥 MESMO AGRUPAMENTO DO TOP10 DE TEMPO ===
    resumo = aplicar_agrupamentos(resumo)

    # Regra de corte (depois do agrupamento!)
    resumo = resumo[resumo['Qtde_OS'] >= 10]

    # Top 3 piores (menor % no tempo)
    top3 = resumo.sort_values('%_No_Tempo').head(3)

    return top3[[
        'Servico_Limpo',
        'Qtde_OS',
        'TempoPadrao',
        'Media_Execucao',
        'Diferenca',
        '%_No_Tempo'
    ]]

def aplicar_agrupamentos(resumo):
    mapa = {
        "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA PAREDE": "LIGAÇÃO NOVA DE ÁGUA",
        "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA PISO": "LIGAÇÃO NOVA DE ÁGUA",
        "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA TOTEM": "LIGAÇÃO NOVA DE ÁGUA",

        "ANÁLISE DE VIABILIDADE DE ABASTECIMENTO": "AVA/AVE",
        "ANÁLISE DE VIABILIDADE DE ESGOTAMENTO": "AVA/AVE",

        "APA - AVALIAÇÃO DE POSSIBILIDADE DE ABASTECIMENTO": "APA/APE",
        "APE - AVALIAÇÃO DE POSSIBILIDADE DE ESGOTAMENTO": "APA/APE",

        "FISCALIZAÇÃO DE CORTE NA REDE COM SUPRESSÃO DE RAMAL": "FISCALIZAÇÃO DE CORTE",
        "FISCALIZAÇÃO DE CORTE NO RAMAL SEM SUPRESSÃO DE RAMAL": "FISCALIZAÇÃO DE CORTE",
        "FISCALIZAÇÃO DE CORTE HIDRÔMETRO": "FISCALIZAÇÃO DE CORTE",
    }

    resumo['Servico_Agrupado'] = resumo['Servico_Limpo'].replace(mapa)

    agrupado = resumo.groupby('Servico_Agrupado').agg(
        Qtde_OS=('Qtde_OS', 'sum'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('Media_Execucao', 'mean'),
        Diferenca=('Diferença', 'mean'),
        Pct_No_Tempo=('%_No_Tempo', 'mean')
    ).reset_index()

    agrupado = agrupado.rename(columns={
        'Servico_Agrupado': 'Servico_Limpo',
        'Pct_No_Tempo': '%_No_Tempo'
    })

    return agrupado
