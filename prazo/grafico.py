import matplotlib.pyplot as plt
import os
import numpy as np

def gerar_grafico(resumo_conc, pasta_saida, conc):
    meses = resumo_conc['Mes'].dt.month_name(locale='pt_BR')
    qtde_os = resumo_conc['Qtde_OS']
    pct_no_prazo = resumo_conc['%_No_Prazo']

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Remover bordas
    for spine in ax.spines.values():
        spine.set_visible(False)

    # --- Barras ---
    bars = ax.bar(meses, qtde_os, color='#1f4e79', label='Qtde de OS')
    ax.set_yticks([])

    # --- Linha dentro da barra ---
    y_linha = qtde_os * (pct_no_prazo / 100)
    ax.plot(meses, y_linha, marker='o', linewidth=2, color='#d97a00',
            label='% Serviços No Prazo')

    # --- Texto da coluna (na base, dentro da barra) ---
    for bar in bars:
        h = bar.get_height()
        valor = f"{h:,.0f}".replace(",", ".") if h >= 1000 else str(int(h))

        ax.text(
            bar.get_x() + bar.get_width()/2,
            h * 0.05,               # <<<<<< NOVO: valor dentro da barra corretamente
            valor,
            ha='center', va='bottom',
            fontsize=10, fontweight='bold',
            color="white"
        )

    # --- Texto da linha ---
    for i, (pct_real, y) in enumerate(zip(pct_no_prazo, y_linha)):
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

    caminho_grafico = os.path.join(pasta_saida, f'{conc}_Prazo_Grafico_6meses.png')
    plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
    plt.close()
    return caminho_grafico

def gerar_grafico_concessionarias(df_filtrado, pasta_saida):

    df_valido = df_filtrado[df_filtrado["StatusPrazo"].isin(["No Prazo", "Fora do Prazo"])]

    resumo = df_valido.groupby("EMPRESA").agg(
        Qtde_OS=("Nº O.S.", "count"),
        No_Prazo=("StatusPrazo", lambda x: (x == "No Prazo").sum())
    ).reset_index()

    resumo["%_No_Prazo"] = round((resumo["No_Prazo"] / resumo["Qtde_OS"]) * 100, 2)
    resumo["%_Fora_Prazo"] = round(100 - resumo["%_No_Prazo"], 2)

    resumo = resumo.sort_values("%_No_Prazo", ascending=False)

    empresas = resumo["EMPRESA"]
    pct_no = resumo["%_No_Prazo"]
    pct_fora = resumo["%_Fora_Prazo"]

    # aumenta o espaço entre grupos
    # ============================
    x = np.arange(0, len(empresas) * 1.4, 1.4)

    largura = 0.55
    desloc = 0.35

    fig, ax = plt.subplots(figsize=(12, 3.0))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_ylim(0, 110)

    # barras
    b1 = ax.bar(x - desloc, pct_no, width=largura, color="#1f77ff", label="% Serv No Prazo")
    b2 = ax.bar(x + desloc, pct_fora, width=largura, color="#002060", label="% Serv Fora do Prazo")

    # textos
    for bar in b1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.2f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    for bar in b2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.2f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    # x-ticks
    ax.set_xticks(x)
    ax.set_xticklabels(empresas, rotation=0, ha="center", fontsize=10)

    ax.set_yticks([])

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center',
               bbox_to_anchor=(0.5, 1.10), ncol=2, frameon=False)

    fig.tight_layout()

    caminho = os.path.join(pasta_saida, "GAB_Concessionarias_Prazo.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close()

    return caminho
