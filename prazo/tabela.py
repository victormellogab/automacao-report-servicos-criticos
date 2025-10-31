import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table

def salvar_tabela_img(df, caminho_arquivo):
    # Renomeia colunas conforme especificação
    df = df.rename(columns={
        df.columns[0]: "Serviços",
        df.columns[1]: "Qtde de OS (Geral)",
        df.columns[2]: "Prazo Padrão (Dias)",
        df.columns[3]: "Média Execução (Dias)",
        df.columns[4]: "Diferença (Dias)",
        df.columns[5]: "% OS no Prazo Padrão"
    })

    # Formatação dos valores
    df_formatado = df.copy()
    df_formatado["Qtde de OS (Geral)"] = df_formatado["Qtde de OS (Geral)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    for col in [
        "Prazo Padrão (Dias)", 
        "Média Execução (Dias)", 
        "Diferença (Dias)"
    ]:
        df_formatado[col] = df_formatado[col].apply(lambda x: f"{x:.2f}".replace(".", ","))

    df_formatado["% OS no Prazo Padrão"] = df_formatado["% OS no Prazo Padrão"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

    # Criar figura exatamente do tamanho da tabela
    fig, ax = plt.subplots(figsize=(10, len(df)*0.6))
    ax.axis('off')

    # Criar tabela
    tabela = plt.table(
        cellText=df_formatado.values,
        colLabels=df_formatado.columns,
        cellLoc='center',
        loc='center'
    )

    # Estilo do cabeçalho
    for (row, col), cell in tabela.get_celld().items():
        if row == 0:  # Cabeçalho
            cell.set_facecolor('#002060')  # Azul escuro
            cell.set_text_props(color='white', weight='bold', fontsize=10)
        else:
            cell.set_text_props(fontsize=9)

        cell.set_edgecolor('black')

    # Ajuste layout
    tabela.scale(1, 1.4)
    plt.tight_layout(pad=0)

    # Salvar sem bordas
    plt.savefig(caminho_arquivo, bbox_inches='tight', dpi=300)
    plt.close()
