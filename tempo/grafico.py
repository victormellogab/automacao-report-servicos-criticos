import matplotlib.pyplot as plt
import os

def gerar_grafico(resumo_conc, pasta_saida, conc):
    meses = resumo_conc['Mes'].dt.month_name(locale='pt_BR')
    qtde_os = resumo_conc['Qtde_OS']
    pct_no_tempo = resumo_conc['%_No_Tempo']

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
    y_linha = qtde_os * (pct_no_tempo / 100)
    ax.plot(meses, y_linha, marker='o', linewidth=2, color='#d97a00',
            label='% Serviços No Tempo')

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

    caminho_grafico = os.path.join(pasta_saida, f'{conc}_Evolucao_Abr-Set_2025.png')
    plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
    plt.close()
    return caminho_grafico
