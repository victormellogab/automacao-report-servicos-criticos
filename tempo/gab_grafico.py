import matplotlib.pyplot as plt
import os
import numpy as np

def gerar_grafico_concessionarias(df, pasta_saida):
    # Agrupar por concessionária
    resumo = df.groupby("EMPRESA").agg(
        Qtde_OS=("Nº O.S.", "count"),
        No_Prazo=("StatusPrazo", lambda x: (x == "No Prazo").sum())
    ).reset_index()

    resumo["%_No_Prazo"] = round((resumo["No_Prazo"] / resumo["Qtde_OS"]) * 100, 2)
    resumo["%_Fora_Prazo"] = 100 - resumo["%_No_Prazo"]

    # Ordenar pela % no prazo (opcional – igual o gráfico da imagem)
    resumo = resumo.sort_values("%_No_Prazo", ascending=False)

    empresas = resumo["EMPRESA"]
    pct_prazo = resumo["%_No_Prazo"]
    pct_fora = resumo["%_Fora_Prazo"]

    x = np.arange(len(empresas))

    fig, ax = plt.subplots(figsize=(10, 3))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Remove bordas
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Barras — % Serviços no Prazo
    bars1 = ax.bar(x, pct_prazo, color="#1f77ff", width=0.6, label="% Serv No Prazo")

    # Barras — % Serviços Fora do Prazo (em cima)
    bars2 = ax.bar(x, pct_fora, bottom=pct_prazo, color="#003399", width=0.6, label="% Serv Fora do Prazo")

    ax.set_xticks(x)
    ax.set_xticklabels(empresas, rotation=45, ha="right")

    # Textos das barras
    for i, (p_p, p_f) in enumerate(zip(pct_prazo, pct_fora)):
        # % No Prazo
        ax.text(i, p_p/2, f"{p_p:.2f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        # % Fora Prazo
        ax.text(i, p_p + p_f/2, f"{p_f:.2f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

    # Legenda
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1], loc="upper center", ncol=2, frameon=False)

    plt.tight_layout()

    caminho = os.path.join(pasta_saida, "GAB_Concessionarias_Prazo.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close()

    return caminho
