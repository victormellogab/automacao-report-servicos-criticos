from config import CONCESSIONARIAS, PASTA_SAIDA
from carregar_tratar_base import carregar_dados
from filtros import filtrar_periodo, excluir_invalidos, filtrar_executados
from top10 import gerar_top10
from top3 import gerar_top3
from grafico import gerar_grafico
import pandas as pd
import matplotlib.pyplot as plt
from tabela import salvar_tabela_img
from card import gerar_cards_os
from medidas import calcular_tempo_padrao_dinamico
from prazo.gab_grafico_prazo import gerar_grafico_concessionarias
import os
from docx import Document

def main():
    # Carregar dados
    pasta_gab = os.path.join(PASTA_SAIDA, "GAB")
    os.makedirs(pasta_gab, exist_ok=True)
    
    df, df_servicos = carregar_dados()

    df = calcular_tempo_padrao_dinamico(df, df_servicos)
    
    # Resumo do mês (contagem OS / % no prazo / % fora)
    print("\n===== Resumo Mês =====")

    for conc in CONCESSIONARIAS:
        df_mes = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-10-01'), pd.to_datetime('2025-10-31'))
        df_mes = df_mes[df_mes['EMPRESA'] == conc]
        df_mes = filtrar_executados(df_mes)
        df_mes = excluir_invalidos(df_mes)

        # Gerar cards
        gerar_cards_os(df_mes, conc, f"{PASTA_SAIDA}/{conc}_Tempo_Cards")

    # Top 10 do mês
    for conc in CONCESSIONARIAS:
        df_top10 = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-10-01'), pd.to_datetime('2025-10-31'))
        df_top10 = excluir_invalidos(df_top10)
        df_top10 = filtrar_executados(df_top10)
        top10 = gerar_top10(df_top10[df_top10['EMPRESA'] == conc])
        salvar_tabela_img(top10, f"{PASTA_SAIDA}/{conc}_Tempo_Top10")

    # Top 3 últimos 3 meses
    for conc in CONCESSIONARIAS:
        df_3meses = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-08-01'), pd.to_datetime('2025-10-31'))
        df_3meses = filtrar_executados(df_3meses)
        df_3meses = excluir_invalidos(df_3meses)
        top3 = gerar_top3(df_3meses[df_3meses['EMPRESA'] == conc])
        salvar_tabela_img(top3, f"{PASTA_SAIDA}/{conc}_Tempo_Top3")

    # Gráfico últimos 6 meses
    for conc in CONCESSIONARIAS:
        df_graf = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-05-01'), pd.to_datetime('2025-10-31'))
        df_graf = df_graf[df_graf['EMPRESA'] == conc]
        df_graf = excluir_invalidos(df_graf)
        df_graf = filtrar_executados(df_graf)
        df_graf['Mes'] = df_graf['DATA_BAIXA'].dt.to_period('M').dt.to_timestamp()
        resumo_conc = df_graf.groupby('Mes').agg(
            Qtde_OS=('Nº O.S.', 'count'),
            No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
        ).reset_index()
        resumo_conc['%_No_Tempo'] = round((resumo_conc['No_Tempo'] / resumo_conc['Qtde_OS']) * 100, 2)
        gerar_grafico(resumo_conc, PASTA_SAIDA, conc)

if __name__ == "__main__":
    main()
