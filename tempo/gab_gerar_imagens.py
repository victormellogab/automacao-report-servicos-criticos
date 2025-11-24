# gerar_imagens_GAB_TEMPO.py
from config import PASTA_SAIDA
from carregar_tratar_base import carregar_dados
from filtros import filtrar_periodo, excluir_invalidos, filtrar_executados
from medidas import gab_calcular_tempo_dax
from top10 import gerar_top10, gerar_top10_com_top3_concessionarias_tempo
from top3 import gerar_top3
from grafico import gerar_grafico, gerar_grafico_concessionarias_tempo
from tabela import salvar_tabela_img, salvar_tabela_top10_expandido_img_tempo
from tabela_gab import salvar_tabela_top3_compacto_tempo
from card import gerar_cards_os
import pandas as pd
import os
from impacto_concessionarias import gerar_imagens_top3_tempo

def main():
    print("\n===== GERANDO CONSOLIDADO GAB - TEMPO PADRÃO =====")

    # Carregar bases
    df, df_servicos = carregar_dados()
    df['TempoPadrao'] = df.apply(lambda x: gab_calcular_tempo_dax(x, df, df_servicos), axis=1)

    # Criar pasta consolidada GAB (caso não exista)
    pasta_gab = os.path.join(PASTA_SAIDA, "GAB")
    os.makedirs(pasta_gab, exist_ok=True)

    # ======== CARDS ========
    df_mes = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-10-01'), pd.to_datetime('2025-10-31'))
    df_mes = excluir_invalidos(df_mes)
    df_mes = filtrar_executados(df_mes)

    gerar_cards_os(df_mes, "GAB", f"{pasta_gab}/GAB_Tempo_Cards")

    # ======== TOP 10 ========
    df_top10 = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-10-01'), pd.to_datetime('2025-10-31'))
    df_top10 = excluir_invalidos(df_top10)
    df_top10 = filtrar_executados(df_top10)
    top10 = gerar_top10(df_top10)
    salvar_tabela_img(top10, f"{pasta_gab}/GAB_Tempo_Top10")

    # === Gerar gráficos detalhados ===
    gerar_imagens_top3_tempo(df_mes, top10, pasta_gab)

    # ======== TOP 10 Detalhado ========
    #top10_expand = gerar_top10_com_top3_concessionarias_tempo(df_top10, df_servicos)
    #salvar_tabela_top10_expandido_img_tempo(top10_expand, f"{pasta_gab}/GAB_Tempo_Top10_Detalhado")

    # ======== TOP 3 (últimos 6 meses) ========
    df_3meses = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-05-01'), pd.to_datetime('2025-10-31'))
    df_3meses = excluir_invalidos(df_3meses)
    df_3meses = filtrar_executados(df_3meses)
    top3 = gerar_top3(df_3meses)
    salvar_tabela_top3_compacto_tempo(top3, f"{pasta_gab}/GAB_Tempo_Top3")

    # ======== GRÁFICO (últimos 6 meses) ========
    df_graf = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-05-01'), pd.to_datetime('2025-10-31'))
    df_graf = excluir_invalidos(df_graf)
    df_graf = filtrar_executados(df_graf)
    df_graf['Mes'] = df_graf['DATA_BAIXA'].dt.to_period('M').dt.to_timestamp()

    resumo = df_graf.groupby('Mes').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        No_Tempo=('StatusTempo', lambda x: (x == 'No Tempo').sum())
    ).reset_index()

    resumo['%_No_Tempo'] = round((resumo['No_Tempo'] / resumo['Qtde_OS']) * 100, 2)
    gerar_grafico(resumo, pasta_gab, "GAB")
    
    gerar_grafico_concessionarias_tempo(df_mes, pasta_gab)

    print("\n✅ Imagens consolidadas GAB (Tempo Padrão) geradas com sucesso!")
    
    gerar_grafico_concessionarias_tempo(df_mes, pasta_gab)

if __name__ == "__main__":
    main()
