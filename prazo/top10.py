import pandas as pd

def gerar_top10_concessionarias(df):
    # Agrupamento por serviço (nível agregado)
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
    ).reset_index()

    # Diferença calculada após o agrupamento
    resumo['Diferenca'] = resumo['Media_Execucao'] - resumo['Prazo_Padrao']

    # % Serviços no Prazo
    resumo['%_No_Prazo'] = round((resumo['No_Prazo'] / resumo['Qtde_OS']) * 100, 2)

    # Ordenar pelos piores desempenhos
    top10 = resumo.sort_values('%_No_Prazo').head(10)

    return top10[['Servico_Limpo', 'Qtde_OS', 'Prazo_Padrao', 'Media_Execucao', 'Diferenca', '%_No_Prazo']]

def gerar_top10(df):
    # Agrupamento por serviço (nível agregado)
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
    ).reset_index()

    # Diferença calculada após o agrupamento
    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['Prazo_Padrao']

    # % Serviços no Prazo
    resumo['%_No_Prazo'] = round((resumo['No_Prazo'] / resumo['Qtde_OS']) * 100, 2)

    # === 🔥 AQUI entra o agrupamento novo que você quer ===
    resumo = aplicar_agrupamentos(resumo)

    # Ordenar pelos piores desempenhos
    top10 = resumo.sort_values('%_No_Prazo').head(10)

    return top10[['Servico_Limpo', 'Qtde_OS', 'Prazo_Padrao', 'Media_Execucao', 'Diferenca', '%_No_Prazo']]

def gerar_top10_com_top3_concessionarias(df, df_servicos):

    # ===== Resumo por SERVIÇO =====
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
    ).reset_index()

    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['Prazo_Padrao']
    resumo['%_No_Prazo'] = round((resumo['No_Prazo'] / resumo['Qtde_OS']) * 100, 2)

    top10 = resumo.sort_values('%_No_Prazo').head(10)

    linhas_final = []

    for _, linha in top10.iterrows():
        serv = linha['Servico_Limpo']

        # Linha principal (serviço)
        linhas_final.append({
            "Tipo": "SERVICO",
            "Servico": serv,
            "Empresa": "",
            "Qtde_OS": linha["Qtde_OS"],
            "Prazo_Padrao": linha["Prazo_Padrao"],
            "Media_Execucao": linha["Media_Execucao"],
            "Diferença": linha["Diferença"],
            "%_No_Prazo": linha["%_No_Prazo"],
            "Impacto": ""
        })

        # Filtrar serviço
        df_serv = df[df['Servico_Limpo'] == serv]

        # ===== TOTAL fora do prazo do SERVIÇO =====
        total_fora = (df_serv["StatusPrazo"] == "Fora do Prazo").sum()
        if total_fora == 0:
            total_fora = 1   # evita divisão por zero

        # ===== AGRUPAR POR EMPRESA =====
        por_emp = df_serv.groupby("EMPRESA").agg(
            Qtde_OS_Empresa=('Nº O.S.', 'count'),
            Media_Execucao=('DiasDeExec', 'mean'),
            No_Prazo=('StatusPrazo', lambda x: (x == "No Prazo").sum()),
            Fora_Prazo=('StatusPrazo', lambda x: (x == "Fora do Prazo").sum())
        ).reset_index()

        por_emp["%_No_Prazo_Empresa"] = round(
            (por_emp["No_Prazo"] / por_emp["Qtde_OS_Empresa"]) * 100, 2
        )

        # IMPACTO CORRETO = % das OS fora do prazo do serviço atribuídas à concessionária
        por_emp["Impacto"] = por_emp["Fora_Prazo"] / total_fora

        # TOP 3 impactantes (AGORA CORRETO)
        top3 = por_emp.sort_values("Impacto", ascending=False).head(3)

        for _, emp in top3.iterrows():

            # ===== Buscar PRAZO PADRÃO correto =====
            prazo_empresa = df_servicos.loc[
                (df_servicos["Serviços"] == serv) &
                (df_servicos["Concessionária"] == emp["EMPRESA"]),
                "Prazo para Empresa"
            ].iloc[0]

            diferenca_emp = emp["Media_Execucao"] - prazo_empresa

            linhas_final.append({
                "Tipo": "EMPRESA",
                "Servico": "",
                "Empresa": emp["EMPRESA"],
                "Qtde_OS": emp["Qtde_OS_Empresa"],
                "Prazo_Padrao": prazo_empresa,
                "Media_Execucao": emp["Media_Execucao"],
                "Diferença": diferenca_emp,
                "%_No_Prazo": emp["%_No_Prazo_Empresa"],
                "Impacto": round(emp["Impacto"] * 100, 2)  # em %
            })

    return pd.DataFrame(linhas_final)

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
