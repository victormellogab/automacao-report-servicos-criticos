import pandas as pd

def gerar_top3(df):
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('TEMPO_EXEC_MIN', 'mean'),
        No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
    ).reset_index()

    # Diferença = Média Execução - Tempo Padrão
    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['TempoPadrao']

    # Filtrar serviços com 10 ou mais OS
    resumo = resumo[resumo['Qtde_OS'] >= 10]

    # % No tempo
    resumo['%_No_Tempo'] = round((resumo['No_Tempo'] / resumo['Qtde_OS']) * 100, 2)

    # Seleciona os 3 piores serviços (menor % no tempo)
    top3 = resumo.sort_values('%_No_Tempo').head(3)

    return top3[['Servico_Limpo','Qtde_OS','TempoPadrao','Media_Execucao','Diferença','%_No_Tempo']]
