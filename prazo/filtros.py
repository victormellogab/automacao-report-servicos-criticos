import pandas as pd

def filtrar_periodo(df, coluna_data, data_inicio, data_fim):
    return df[(df[coluna_data] >= data_inicio) & (df[coluna_data] <= data_fim)]

'''def excluir_invalidos(df):
    df = df[(df['AREA_EXEC'] != 'ENGENHARIA') & (df['Área Exec.'] != 'ENGENHARIA')]
    return df
'''