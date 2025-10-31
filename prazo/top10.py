import pandas as pd

def gerar_top10(df):
    resumo = df.groupby('Servico_Limpo').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        Prazo_Padrao=('PrazoPadrao', 'mean'),
        Media_Execucao=('DiasDeExec', 'mean'),
        Diferença=('DiasDeExec', lambda x: x.mean() - df.loc[x.index, 'PrazoPadrao'].mean()),
        No_Prazo=('StatusPrazo', lambda x: (x=='No Prazo').sum())
    ).reset_index()

    resumo['%_No_Prazo'] = round((resumo['No_Prazo'] / resumo['Qtde_OS']) * 100, 2)
    top10 = resumo.sort_values('%_No_Prazo').head(10)
    return top10[['Servico_Limpo','Qtde_OS','Prazo_Padrao','Media_Execucao','Diferença','%_No_Prazo']]
