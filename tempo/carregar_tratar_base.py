import pandas as pd
from utils import normalizar_texto
from config import CAMINHO_INOVA, CAMINHO_SERVICOS

def carregar_dados():
    df = pd.read_excel(CAMINHO_INOVA, engine='openpyxl')
    df_servicos = pd.read_csv(CAMINHO_SERVICOS, sep=';', encoding='latin1')

    df.columns = df.columns.str.strip()
    df_servicos.columns = df_servicos.columns.str.strip()

    df = normalizar_texto(df, ['EMPRESA', 'AREA_EXEC', 'Área Exec.', 'Servico_Limpo'])
    df_servicos = normalizar_texto(df_servicos, ['Serviços', 'Concessionária'])

    df['DATA_HORA_INCL'] = pd.to_datetime(df['DATA_HORA_INCL'], dayfirst=True, errors='coerce')
    df['DATA_BAIXA'] = pd.to_datetime(df['DATA_BAIXA'], dayfirst=True, errors='coerce')

    df = df[df['DATA_HORA_INCL'].notna() & df['DATA_BAIXA'].notna()]

    return df, df_servicos
