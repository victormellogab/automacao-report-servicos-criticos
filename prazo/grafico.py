import matplotlib.pyplot as plt
import os

def gerar_grafico(resumo_conc, pasta_saida, conc):
    meses = resumo_conc['Mes'].dt.month_name(locale='pt_BR')
    qtde_os = resumo_conc['Qtde_OS']
    pct_no_prazo = resumo_conc['%_No_Prazo']

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    ax2 = ax1.twinx()
    ax2.set_facecolor('white')

    # Remover borda
    for spine in ax1.spines.values(): spine.set_visible(False)
    for spine in ax2.spines.values(): spine.set_visible(False)

    # Barras
    bars = ax1.bar(meses, qtde_os, label='Qtde de OS', color='#1f4e79')
    ax1.tick_params(axis='x', rotation=0)
    ax1.set_yticks([])

    for bar in bars:
        h = bar.get_height()
        valor = f"{h:,.0f}".replace(",", ".") if h >= 1000 else str(int(h))
        ax1.text(bar.get_x() + bar.get_width()/2, h/2, valor, ha='center', va='center',
                 fontsize=10, fontweight='bold', color="white")

    # Linha
    ax2.plot(meses, pct_no_prazo, marker='o', linewidth=2, label='% Serviços No Prazo', color='#d97a00')
    ax2.set_yticks([])

    for i, pct in enumerate(pct_no_prazo):
        ax2.text(i, pct + 0.2, f'{pct}%', ha='center', va='bottom', fontsize=10, fontweight='bold',
                 color='#4a4a4a', bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='none', alpha=0.9))

    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.07), ncol=2, frameon=False)
    fig.tight_layout()

    caminho_grafico = os.path.join(pasta_saida, f'{conc}_Evolucao_Abr-Set_2025.png')
    plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
    plt.close()
    return caminho_grafico
