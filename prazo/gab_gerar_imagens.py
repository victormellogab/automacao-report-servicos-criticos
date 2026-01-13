# gerar_imagens_GAB.py
from config_gab import PASTA_SAIDA, CONCESSIONARIAS
from carregar_tratar_base import carregar_dados
from filtros import filtrar_periodo
from medidas import calcular_dias_exec, criar_status_prazo, gab_calcular_prazo_dax
from top10 import gerar_top10
from top3 import gerar_top3
from grafico import gerar_grafico, gerar_grafico_concessionarias
from tabela import salvar_tabela_img
from tabela_gab import salvar_tabela_top3_compacto
from card import gerar_cards_os
import pandas as pd
import os
from impacto_concessionarias import gerar_imagens_top3_de_top10

def main():
    print("\n===== GERANDO CONSOLIDADO GAB =====")

    df, df_servicos = carregar_dados()

    # 🔹 FILTRO GLOBAL DAS CONCESSIONÁRIAS (controle via config.py)
    df = df[df['EMPRESA'].isin(CONCESSIONARIAS)].copy()

    # Cria subpasta GAB dentro da pasta de saída
    pasta_gab = os.path.join(PASTA_SAIDA, "GAB")
    os.makedirs(pasta_gab, exist_ok=True)

    # ======== cards ========
    df_mes = filtrar_periodo(
        df,
        'DATA_BAIXA',
        pd.to_datetime('2025-12-01'),
        pd.to_datetime('2025-12-31')
    )
    df_mes = calcular_dias_exec(df_mes, 'DATA_HORA_INCL', 'DATA_BAIXA')
    df_mes['PrazoPadrao'] = df_mes.apply(
        lambda x: gab_calcular_prazo_dax(x, df_mes, df_servicos),
        axis=1
    )
    df_mes = df_mes[df_mes['PrazoPadrao'].notna()]
    df_mes = criar_status_prazo(df_mes)

    gerar_cards_os(df_mes, "GAB", f"{pasta_gab}/GAB_Prazo_Cards")
    
    # ======== top10 normal ========
    top10_normal = gerar_top10(df_mes)
    salvar_tabela_img(top10_normal, f"{pasta_gab}/GAB_Prazo_Top10")
    
    # gráficos detalhados por concessionária no top 3 do top 10
    caminhos_imagens = gerar_imagens_top3_de_top10(df_mes, top10_normal, pasta_gab)
    print("Imagens de impacto geradas:", caminhos_imagens)

    # ======== top6 ========
    df_6meses = filtrar_periodo(
        df,
        'DATA_BAIXA',
        pd.to_datetime('2025-07-01'),
        pd.to_datetime('2025-12-31')
    )
    df_6meses = calcular_dias_exec(df_6meses, 'DATA_HORA_INCL', 'DATA_BAIXA')
    df_6meses['PrazoPadrao'] = df_6meses.apply(
        lambda x: gab_calcular_prazo_dax(x, df_6meses, df_servicos),
        axis=1
    )
    df_6meses = df_6meses[df_6meses['PrazoPadrao'].notna()]
    df_6meses = criar_status_prazo(df_6meses)

    top3 = gerar_top3(df_6meses)
    salvar_tabela_top3_compacto(top3, f"{pasta_gab}/GAB_Prazo_Top3")
    
    # ======== gráfico 6 meses ========
    df_graf = filtrar_periodo(
        df,
        'DATA_BAIXA',
        pd.to_datetime('2025-07-01'),
        pd.to_datetime('2025-12-31')
    )
    df_graf = calcular_dias_exec(df_graf, 'DATA_HORA_INCL', 'DATA_BAIXA')
    df_graf['PrazoPadrao'] = df_graf.apply(
        lambda x: gab_calcular_prazo_dax(x, df_graf, df_servicos),
        axis=1
    )
    df_graf = df_graf[df_graf['PrazoPadrao'].notna()]
    df_graf = criar_status_prazo(df_graf)
    df_graf['Mes'] = df_graf['DATA_BAIXA'].dt.to_period('M').dt.to_timestamp()

    resumo = df_graf.groupby('Mes').agg(
        Qtde_OS=('Nº O.S.', 'count'),
        No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
    ).reset_index()

    resumo['%_No_Prazo'] = round(
        (resumo['No_Prazo'] / resumo['Qtde_OS']) * 100,
        2
    )

    gerar_grafico(resumo, pasta_gab, "GAB")

    print("\n✅ Imagens consolidadas GAB geradas com sucesso!")
    
    gerar_grafico_concessionarias(df_mes, pasta_gab)

if __name__ == "__main__":
    main()
