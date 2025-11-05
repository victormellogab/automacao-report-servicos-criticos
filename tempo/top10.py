import pandas as pd

def gerar_top10(df):
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        TempoPadrao=('TempoPadrao', 'mean'),
        Media_Execucao=('TEMPO_EXEC_MIN', 'mean'),
        No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
    ).reset_index()

    resumo['Diferença'] = resumo['Media_Execucao'] - resumo['TempoPadrao']
    resumo['%_No_Tempo'] = round((resumo['No_Tempo'] / resumo['Qtde_OS']) * 100, 2)

    top10 = resumo.sort_values('%_No_Tempo').head(10)
    return top10[['Servico_Limpo','Qtde_OS','TempoPadrao','Media_Execucao','Diferença','%_No_Tempo']]
