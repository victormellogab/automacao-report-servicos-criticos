import pandas as pd

def gerar_top3(df):
    # Agrupamento por serviço (nível agregado)
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
    ).reset_index()

    # Calcular diferença depois da agregação
    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['Prazo_Padrao']

    # Filtrar serviços com pelo menos 10 OS
    resumo = resumo[resumo['Qtde_OS'] >= 10]

    # Calcular percentual no prazo
    resumo['%_No_Prazo'] = round((resumo['No_Prazo'] / resumo['Qtde_OS']) * 100, 2)

    # Selecionar os 3 piores desempenhos
    top3 = resumo.sort_values('%_No_Prazo').head(3)

    return top3[['Servico_Limpo', 'Qtde_OS', 'Prazo_Padrao', 'Media_Execucao', 'Diferença', '%_No_Prazo']]
