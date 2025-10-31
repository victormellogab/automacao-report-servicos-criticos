import pandas as pd
import math

# Normalizar colunas de texto
def normalizar_texto(df, colunas):
    for col in colunas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df
