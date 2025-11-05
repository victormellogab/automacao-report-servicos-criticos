from config import CONCESSIONARIAS, PASTA_SAIDA
from carregamento import carregar_dados
from filtros import filtrar_periodo, excluir_invalidos, filtrar_executados
from medidas import calcular_dias_exec, criar_status_prazo, criar_prazo_dict, calcular_prazo_dax
from top10 import gerar_top10
from top3 import gerar_top3
from grafico import gerar_grafico
import pandas as pd
import matplotlib.pyplot as plt
from tabela import salvar_tabela_img
from card import gerar_cards_os

def main():
    # Carregar dados
    df, df_servicos = carregar_dados()

    # Criar dicionário de prazo
    prazo_dict = criar_prazo_dict(df_servicos)
    
    # Resumo do mês (contagem OS / % no prazo / % fora)
    print("\n===== Resumo Setembro 2025 =====")

    for conc in CONCESSIONARIAS:
        df_mes = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-09-01'), pd.to_datetime('2025-09-30'))
        df_mes = df_mes[df_mes['EMPRESA'] == conc]
        df_mes = filtrar_executados(df_mes)
        df_mes = excluir_invalidos(df_mes)
        df_mes = calcular_dias_exec(df_mes, 'DATA_HORA_INCL', 'DATA_BAIXA')
        df_mes['PrazoPadrao'] = df_mes.apply(lambda x: calcular_prazo_dax(x, prazo_dict, df_servicos), axis=1)
        df_mes = df_mes[df_mes['PrazoPadrao'].notna()]

        # Gerar cards
        gerar_cards_os(df_mes, conc, f"{PASTA_SAIDA}/{conc}_Resumo_Setembro")
'''
    # Top 10 do mês
    caminho_top10 = "top10_setembro.xlsx"
    for conc in CONCESSIONARIAS:
        df_top10 = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-09-01'), pd.to_datetime('2025-09-30'))
        df_top10 = excluir_invalidos(df_top10)
        df_top10 = calcular_dias_exec(df_top10, 'DATA_HORA_INCL', 'DATA_BAIXA')
        df_top10['PrazoPadrao'] = df_top10.apply(lambda x: calcular_prazo_dax(x, prazo_dict, df_servicos), axis=1)
        df_top10 = df_top10[df_top10['PrazoPadrao'].notna()]
        df_top10 = criar_status_prazo(df_top10)
        top10 = gerar_top10(df_top10[df_top10['EMPRESA'] == conc])
        salvar_tabela_img(top10, f"{PASTA_SAIDA}/{conc}_Top10_Setembro")

    # Top 3 últimos 3 meses
    for conc in CONCESSIONARIAS:
        df_3meses = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-07-01'), pd.to_datetime('2025-09-30'))
        df_3meses = excluir_invalidos(df_3meses)
        df_3meses = calcular_dias_exec(df_3meses, 'DATA_HORA_INCL', 'DATA_BAIXA')
        df_3meses['PrazoPadrao'] = df_3meses.apply(lambda x: calcular_prazo_dax(x, prazo_dict, df_servicos), axis=1)
        df_3meses = df_3meses[df_3meses['PrazoPadrao'].notna()]
        df_3meses = criar_status_prazo(df_3meses)
        top3 = gerar_top3(df_3meses[df_3meses['EMPRESA'] == conc])
        salvar_tabela_img(top3, f"{PASTA_SAIDA}/{conc}_Top3_3Meses")

    # Gráficos
    for conc in CONCESSIONARIAS:
        df_graf = filtrar_periodo(df, 'DATA_BAIXA', pd.to_datetime('2025-04-01'), pd.to_datetime('2025-09-30'))
        df_graf = df_graf[df_graf['EMPRESA'] == conc]
        df_graf = excluir_invalidos(df_graf)
        df_graf = calcular_dias_exec(df_graf, 'DATA_HORA_INCL', 'DATA_BAIXA')
        df_graf['PrazoPadrao'] = df_graf.apply(lambda x: calcular_prazo_dax(x, prazo_dict, df_servicos), axis=1)
        df_graf = df_graf[df_graf['PrazoPadrao'].notna()]
        df_graf = criar_status_prazo(df_graf)
        df_graf['Mes'] = df_graf['DATA_BAIXA'].dt.to_period('M').dt.to_timestamp()
        resumo_conc = df_graf.groupby('Mes').agg(
            Qtde_OS=('Nº O.S.', 'count'),
            No_Prazo=('StatusPrazo', lambda x: (x == 'No Prazo').sum())
        ).reset_index()
        resumo_conc['%_No_Prazo'] = round((resumo_conc['No_Prazo'] / resumo_conc['Qtde_OS']) * 100, 2)
        gerar_grafico(resumo_conc, PASTA_SAIDA, conc)
'''
if __name__ == "__main__":
    main()
