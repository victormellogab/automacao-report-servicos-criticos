import pandas as pd

def gerar_top10(df):
    # Agrupamento por serviço (nível agregado)
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('TEMPO_EXEC_MIN', 'mean'),
        No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
    ).reset_index()

    # Diferença calculada
    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['TempoPadrao']

    # % Serviços no Tempo Padrão
    resumo['%_No_Tempo'] = round((resumo['No_Tempo'] / resumo['Qtde_OS']) * 100, 2)

    # === AGRUPAMENTO IGUAL AO PRAZO ===
    resumo = aplicar_agrupamentos(resumo)

    # Ordenar pelos piores desempenhos
    top10 = resumo.sort_values('%_No_Tempo').head(10)

    # *** IMPORTANTE: aqui o nome correto é DIFERENCA (sem acento) ***
    return top10[['Servico_Limpo', 'Qtde_OS', 'TempoPadrao', 'Media_Execucao', 'Diferenca', '%_No_Tempo']]


def aplicar_agrupamentos(resumo):
    # Mapa igual ao do PRAZO
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

    # Aplica substituição
    resumo['Servico_Agrupado'] = resumo['Servico_Limpo'].replace(mapa)

    # Reagrupamento com colunas corretas do TEMPO
    agrupado = resumo.groupby('Servico_Agrupado').agg(
        Qtde_OS=('Qtde_OS', 'sum'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('Media_Execucao', 'mean'),
        Diferenca=('Diferença', 'mean'),      # ← aqui vira "Diferenca"
        Pct_No_Tempo=('%_No_Tempo', 'mean')
    ).reset_index()

    # Renomear para manter consistente
    agrupado = agrupado.rename(columns={
        'Servico_Agrupado': 'Servico_Limpo',
        'Pct_No_Tempo': '%_No_Tempo'
    })

    return agrupado


def gerar_top10_com_top3_concessionarias_tempo(df, df_servicos):

    # ===== Resumo por SERVIÇO =====
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('TEMPO_EXEC_MIN', 'mean'),
        No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
    ).reset_index()

    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['TempoPadrao']
    resumo['%_No_Tempo'] = round((resumo['No_Tempo'] / resumo['Qtde_OS']) * 100, 2)

    top10 = resumo.sort_values('%_No_Tempo').head(10)

    linhas_final = []

    for _, linha in top10.iterrows():
        serv = linha['Servico_Limpo']

        # Linha principal
        linhas_final.append({
            "Tipo": "SERVICO",
            "Servico": serv,
            "Empresa": "",
            "Qtde_OS": linha["Qtde_OS"],
            "TempoPadrao": linha["TempoPadrao"],
            "Media_Execucao": linha["Media_Execucao"],
            "Diferença": linha["Diferença"],
            "%_No_Tempo": linha["%_No_Tempo"],
            "Impacto": ""
        })

        # Filtrar serviço
        df_serv = df[df['Servico_Limpo'] == serv]

        # Total fora do tempo do serviço
        total_fora = (df_serv["StatusTempo"] == "Fora do Tempo").sum()
        if total_fora == 0:
            total_fora = 1

        # Agrupar por empresa
        por_emp = df_serv.groupby("EMPRESA").agg(
            Qtde_OS_Empresa=('Nº O.S.', 'count'),
            Media_Execucao=('TEMPO_EXEC_MIN', 'mean'),
            No_Tempo=('StatusTempo', lambda x: (x == "No Tempo").sum()),
            Fora_Tempo=('StatusTempo', lambda x: (x == "Fora do Tempo").sum())
        ).reset_index()

        por_emp["%_No_Tempo_Empresa"] = round(
            (por_emp["No_Tempo"] / por_emp["Qtde_OS_Empresa"]) * 100, 2
        )

        # impacto correto
        por_emp["Impacto"] = por_emp["Fora_Tempo"] / total_fora

        # top3
        top3 = por_emp.sort_values("Impacto", ascending=False).head(3)

        for _, emp in top3.iterrows():

            # Buscar tempo padrão correto na tabela df_servicos
            tempo_empresa = df_servicos.loc[
                (df_servicos["Serviços"] == serv) &
                (df_servicos["Concessionária"] == emp["EMPRESA"]),
                "Tempo Padrão"
            ].iloc[0]

            diferenca_emp = emp["Media_Execucao"] - tempo_empresa

            linhas_final.append({
                "Tipo": "EMPRESA",
                "Servico": "",
                "Empresa": emp["EMPRESA"],
                "Qtde_OS": emp["Qtde_OS_Empresa"],
                "TempoPadrao": tempo_empresa,
                "Media_Execucao": emp["Media_Execucao"],
                "Diferença": diferenca_emp,
                "%_No_Tempo": emp["%_No_Tempo_Empresa"],
                "Impacto": round(emp["Impacto"] * 100, 2)
            })

    return pd.DataFrame(linhas_final)
