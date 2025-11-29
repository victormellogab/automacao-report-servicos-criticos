import matplotlib.pyplot as plt
import os
import numpy as np

def gerar_grafico(resumo_conc, pasta_saida, conc):
    meses = resumo_conc['Mes'].dt.month_name(locale='pt_BR')
    qtde_os = resumo_conc['Qtde_OS']
    pct_no_tempo = resumo_conc['%_No_Tempo']  # ✅ Agora correto

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Remover bordas
    for spine in ax.spines.values():
        spine.set_visible(False)

    # --- Barras ---
    bars = ax.bar(meses, qtde_os, color='#1f4e79', label='Qtde de OS')
    ax.set_yticks([])

    # --- Linha (convertendo % para altura relativa) ---
    y_linha = qtde_os * (pct_no_tempo / 100)
    ax.plot(meses, y_linha, marker='o', linewidth=2, color='#d97a00',
            label='% Serviços No Tempo')

    # --- Texto dentro das barras ---
    for bar in bars:
        h = bar.get_height()
        valor = f"{h:,.0f}".replace(",", ".") if h >= 1000 else str(int(h))
        ax.text(
            bar.get_x() + bar.get_width()/2,
            h*0.05,
            valor,
            ha='center', va='bottom',
            fontsize=10, fontweight='bold',
            color="white"
        )

    # --- Texto da linha (valores da % no tempo) ---
    for i, (pct_real, y) in enumerate(zip(pct_no_tempo, y_linha)):
        ax.text(
            i, y + (qtde_os[i] * 0.05),
            f'{pct_real}%',
            ha='center', va='bottom',
            fontsize=10, fontweight='bold',
            color='#4a4a4a',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='none', alpha=0.9)
        )

    plt.subplots_adjust(bottom=0.22)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1], loc='upper center', bbox_to_anchor=(0.5, 1.07),
            ncol=2, frameon=False)

    fig.tight_layout()

    caminho_grafico = os.path.join(pasta_saida, f'{conc}_Tempo_Grafico_6meses.png')
    plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
    plt.close()
    return caminho_grafico

def gerar_grafico_concessionarias_tempo(df_filtrado, pasta_saida):
    """
    Gráfico por concessionária usando StatusTempo — mesmo layout do gráfico de PRAZO.
    """

    # Filtrar OS válidas para TEMPO
    df_valido = df_filtrado[df_filtrado["StatusTempo"].isin(["No Tempo", "Fora do Tempo"])]

    # Agrupar por concessionária
    resumo = df_valido.groupby("EMPRESA").agg(
        Qtde_OS=("Nº O.S.", "count"),
        No_Tempo=("StatusTempo", lambda x: (x == "No Tempo").sum())
    ).reset_index()

    # Calcular % (igual ao BI)
    resumo["%_No_Tempo"] = round((resumo["No_Tempo"] / resumo["Qtde_OS"]) * 100, 2)
    resumo["%_Fora_Tempo"] = round(100 - resumo["%_No_Tempo"], 2)

    # Ordenar melhor → pior
    resumo = resumo.sort_values("%_No_Tempo", ascending=False)

    empresas = resumo["EMPRESA"]
    pct_no = resumo["%_No_Tempo"]
    pct_fora = resumo["%_Fora_Tempo"]

    # Aumentar espaço entre GRUPOS (mesmo truque do PRAZO)
    # ============================
    x = np.arange(0, len(empresas) * 1.8, 1.8)

    largura = 0.55     # grossura das barras
    desloc = 0.35      # separação entre as 2 barras do grupo

    # Figura achatada
    fig, ax = plt.subplots(figsize=(12, 3.0))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_ylim(0, 110)

    # Barras (idêntico ao layout de PRAZO)
    b1 = ax.bar(x - desloc, pct_no, width=largura, color="#1f77ff", label="% Serv No Tempo")
    b2 = ax.bar(x + desloc, pct_fora, width=largura, color="#002060", label="% Serv Fora do Tempo")

    # Labels
    for bar in b1:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2,
            h + 1,
            f"{h:.2f}%",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold"
        )

    for bar in b2:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2,
            h + 1,
            f"{h:.2f}%",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold"
        )

    # Labels no eixo X
    ax.set_xticks(x)
    ax.set_xticklabels(empresas, rotation=0, ha="center", fontsize=10)

    ax.set_yticks([])

    # Legenda superior (igual ao de PRAZO)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center',
               bbox_to_anchor=(0.5, 1.10), ncol=2, frameon=False)

    fig.tight_layout()

    caminho = os.path.join(pasta_saida, "GAB_Concessionarias_Tempo.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close()

    return caminho
