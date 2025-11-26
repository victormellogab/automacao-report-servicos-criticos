import pandas as pd

def gerar_top3(df):
    # Agrupamento inicial por serviço
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
    ).reset_index()

    # Diferença
    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['Prazo_Padrao']

    # % no prazo
    resumo['%_No_Prazo'] = round(
        (resumo['No_Prazo'] / resumo['Qtde_OS']) * 100, 2
    )

    # === 🔥 APLICAR O MESMO AGRUPAMENTO DO TOP10 ===
    resumo = aplicar_agrupamentos(resumo)

    # Regra de corte (depois do agrupamento!)
    resumo = resumo[resumo['Qtde_OS'] >= 10]

    # Top 3 piores
    top3 = resumo.sort_values('%_No_Prazo').head(3)

    return top3[[
        'Servico_Limpo',
        'Qtde_OS',
        'Prazo_Padrao',
        'Media_Execucao',
        'Diferenca',
        '%_No_Prazo'
    ]]

def aplicar_agrupamentos(resumo):
    # Mapeamento dos grupos desejados
    mapa = {
        "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA PAREDE": "LIGAÇÃO NOVA DE ÁGUA",
        "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA PISO": "LIGAÇÃO NOVA DE ÁGUA",
        "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA TOTEM": "LIGAÇÃO NOVA DE ÁGUA",

        "ANÁLISE DE VIABILIDADE DE ABASTECIMENTO": "AVA/AVE",
        "ANÁLISE DE VIABILIDADE DE ESGOTAMENTO": "AVA/AVE",

        "CONSERTO DE VAZAMENTO EM REDE ÁGUA": "CONSERTO DE VAZAMENTO",
        "CONSERTO DE VAZAMENTO EM RAMAL ÁGUA": "CONSERTO DE VAZAMENTO",
        "CONSERTO DE VAZAMENTO NO CAVALETE": "CONSERTO DE VAZAMENTO",

        "APA - AVALIAÇÃO DE POSSIBILIDADE DE ABASTECIMENTO": "APA/APE",
        "APE - AVALIAÇÃO DE POSSIBILIDADE DE ESGOTAMENTO": "APA/APE",

        "FISCALIZAÇÃO DE CORTE NA REDE COM SUPRESSÃO DE RAMAL": "FISCALIZAÇÃO DE CORTE",
        "FISCALIZAÇÃO DE CORTE NO RAMAL SEM SUPRESSÃO DE RAMAL": "FISCALIZAÇÃO DE CORTE",
        "FISCALIZAÇÃO DE CORTE HIDRÔMETRO": "FISCALIZAÇÃO DE CORTE",

        "SUSPENSÃO DE FORNECIMENTO NO HD": "SUSPENSÃO",
        "SUSPENSÃO DE FORNECIMENTO NO RAMAL": "SUSPENSÃO",

        "RELIGAÇÃO NO HD": "RELIGAÇÃO",
        "RELIGAÇÃO NO RAMAL": "RELIGAÇÃO",
    }

    # Aplica substituição (serviços fora do mapa permanecem iguais)
    resumo['Servico_Agrupado'] = resumo['Servico_Limpo'].replace(mapa)

    # Agora reagrupa usando o nome novo
    agrupado = resumo.groupby('Servico_Agrupado').agg(
        Qtde_OS=('Qtde_OS', 'sum'),
        Prazo_Padrao=('Prazo_Padrao', 'mean'),        # média simples
        Media_Execucao=('Media_Execucao', 'mean'),    # média simples
        Diferenca=('Diferença', 'mean'),              # média simples (coerente)
        Pct_No_Prazo=('%_No_Prazo', 'mean')           # média simples
    ).reset_index()

    # Renomeia para manter compatibilidade com o restante do código
    agrupado = agrupado.rename(columns={
        'Servico_Agrupado': 'Servico_Limpo',
        'Pct_No_Prazo': '%_No_Prazo'
    })

    return agrupado
