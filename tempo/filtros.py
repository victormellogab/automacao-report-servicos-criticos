import pandas as pd

def filtrar_periodo(df, coluna_data, data_inicio, data_fim):
    return df[(df[coluna_data] >= data_inicio) & (df[coluna_data] <= data_fim)]

def excluir_invalidos(df):
    df = df[(df['AREA_EXEC'] != 'ENGENHARIA') & (df['Área Exec.'] != 'ENGENHARIA')]
    df = df[df['DH_EXEC_INI_REL'].notna() & df['DH_EXEC_FIM_REL'].notna()]
    return df

def filtrar_executados(df):
    return df[df['OrigemData'] == 'Executado']
