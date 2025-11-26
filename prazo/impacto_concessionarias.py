# impacto_concessionarias.py
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from textwrap import shorten

# (Reutilize o mesmo mapa que você já tem em aplicar_agrupamentos)
MAPA_AGRUPAMENTO = {
    "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA PAREDE": "LIGAÇÃO NOVA DE ÁGUA",
    "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA PISO": "LIGAÇÃO NOVA DE ÁGUA",
    "LIGAÇÃO NOVA DE ÁGUA C/ CAIXA PROTETORA TOTEM": "LIGAÇÃO NOVA DE ÁGUA",

    "ANÁLISE DE VIABILIDADE DE ABASTECIMENTO": "AVA/AVE",
    "ANÁLISE DE VIABILIDADE DE ESGOTAMENTO": "AVA/AVE",

    "CONSERTO DE VAZAMENTO EM REDE ÁGUA": "CONSERTO DE VAZAMENTO",
    "CONSERTO DE VAZAMENTO EM RAMAL ÁGUA": "CONSERTO DE VAZAMENTO",
    "CONSERTO DE VAZAMENTO NO CAVALETE": "CONSERTO DE VAZAMENTO",

    "APA - AVALIAÇÃO DE POSSIBILIDADE DE ABASTECIMENTO": "APA/APE",
    "APE - AVALIAÇÃO DE POSSIBILIDADE DE ESGOTAMENTO": "APA/APE",

    "FISCALIZAÇÃO DE CORTE NA REDE COM SUPRESSÃO DE RAMAL": "FISCALIZAÇÃO DE CORTE",
    "FISCALIZAÇÃO DE CORTE NO RAMAL SEM SUPRESSÃO DE RAMAL": "FISCALIZAÇÃO DE CORTE",
    "FISCALIZAÇÃO DE CORTE HIDRÔMETRO": "FISCALIZAÇÃO DE CORTE",

    "SUSPENSÃO DE FORNECIMENTO NO HD": "SUSPENSÃO",
    "SUSPENSÃO DE FORNECIMENTO NO RAMAL": "SUSPENSÃO",

    "RELIGAÇÃO NO HD": "RELIGAÇÃO",
    "RELIGAÇÃO NO RAMAL": "RELIGAÇÃO",
}

def _aplicar_mapa_no_df_servicos(df):
    """
    Garante coluna Servico_Agrupado no df original (df_mes).
    Se o serviço não estiver no mapa, mantém o nome original.
    """
    df = df.copy()
    df['Servico_Agrupado'] = df['Servico_Limpo'].replace(MAPA_AGRUPAMENTO)
    return df

def extrair_top3_concessionarias_por_servico(df_mes, top10_df, n=3):
    """
    Para cada serviço do Top10 (já agrupado),
    extrai top 4 concessionárias que MAIS contribuíram para os ATRASOS.
    """
    df = _aplicar_mapa_no_df_servicos(df_mes)

    resultados = {}

    for _, row in top10_df.head(4).iterrows():
        servico = row['Servico_Limpo']

        # Filtra o serviço agrupado
        df_serv = df[df['Servico_Agrupado'] == servico].copy()

        if df_serv.empty:
            resultados[servico] = {
                'total_os': 0,
                'df_top': pd.DataFrame(columns=['EMPRESA', 'Qtde_Fora', 'Impacto_Pct']),
                'restantes_os': 0
            }
            continue

        # ===============================
        # 🔥 Filtrar SOMENTE fora do prazo
        # ===============================
        df_fora = df_serv[df_serv['StatusPrazo'] == 'Fora do Prazo'].copy()

        if df_fora.empty:
            # nenhum atraso → evita erro e mostra zeros
            resultados[servico] = {
                'total_os': 0,
                'df_top': pd.DataFrame(columns=['EMPRESA', 'Qtde_Fora', 'Impacto_Pct']),
                'restantes_os': 0
            }
            continue

        # Agrupar atrasos por empresa
        conc = df_fora.groupby('EMPRESA').agg(
            Qtde_Fora=('Nº O.S.', 'count')
        ).reset_index()

        total_fora = conc['Qtde_Fora'].sum()

        # Impacto real nos atrasos
        conc['Impacto_Pct'] = (conc['Qtde_Fora'] / total_fora * 100).round(2)

        # Top 3 impactantes
        conc = conc.sort_values('Impacto_Pct', ascending=False).reset_index(drop=True)
        df_top = conc.head(n).copy()

        restantes_os = total_fora - df_top['Qtde_Fora'].sum()

        resultados[servico] = {
            'total_os': int(total_fora),   # << agora mostra OS fora do prazo!
            'df_top': df_top.rename(columns={'Qtde_Fora': 'Qtde_OS'}),
            'restantes_os': int(restantes_os)
        }

    return resultados


def gerar_imagem_impacto(servico, info, pasta_saida, largura=1200, altura=600):
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    from matplotlib.patches import FancyBboxPatch

    total_os = info["total_os"]
    df_top = info["df_top"].copy()
    restantes_os = info["restantes_os"]

    # === Outras ===
    if restantes_os > 0:
        impacto_rest = (restantes_os / total_os) * 100
        impacto_rest = np.floor(impacto_rest * 100) / 100
        df_top.loc[len(df_top)] = [
            "Outras",
            restantes_os,
            impacto_rest
        ]

    # === Impacto formatado ===
    df_top["Impacto_Pct"] = df_top["Impacto_Pct"].apply(
        lambda x: np.floor(float(x) * 100) / 100
    )

    # === Escala proporcional das barras ===
    max_pct = df_top["Impacto_Pct"].max()

    # controla o "zoom visual" da barra (ajuste fino)
    ZOOM = 0.85   # experimente entre 0.8 e 0.9
    MIN_LARGURA = 0.28   # ajuste fino: 0.10 ~ 0.14 costumam funcionar bem
    
    df_top["Largura"] = (
        MIN_LARGURA
        + (df_top["Impacto_Pct"] / max_pct) * (ZOOM - MIN_LARGURA)
    )

    # === Caminho da imagem ===
    os.makedirs(pasta_saida, exist_ok=True)
    arquivo = f"{servico.replace('/', '_').replace(' ', '_')}_Impacto_Concessionarias.png"
    caminho = os.path.join(pasta_saida, arquivo)

    # === Figure ===
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    fig, ax = plt.subplots(figsize=(largura/100, altura/100))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.axis("off")

    # === TÍTULO (Estilo A1) ===
    ax.text(0.02, 0.92, servico, fontsize=24, fontweight="bold", ha="left")
    ax.text(0.02, 0.86, f"{total_os:,d} OS | Fora do Prazo".replace(",", "."),
            fontsize=18, fontweight="regular", ha="left")

    # Layout
    y_start = 0.70
    y_gap = 0.17
    barra_altura = 0.10

    # === Função de gradiente (CORRIGIDA) ===
    def gradiente(ax, x, y, w, h, cor_escura, cor_clara):
        steps = 80
        slice_w = w / steps

        for s in range(steps):
            frac = s / (steps - 1)

            # Interpolação real
            r = int(cor_escura[0] + frac * (cor_clara[0] - cor_escura[0]))
            g = int(cor_escura[1] + frac * (cor_clara[1] - cor_escura[1]))
            b = int(cor_escura[2] + frac * (cor_clara[2] - cor_escura[2]))
            color = f"#{r:02X}{g:02X}{b:02X}"

            ax.add_patch(FancyBboxPatch(
                (x + slice_w * s, y),
                slice_w + 0.002,
                h,
                boxstyle="round,pad=0.01" if s == steps - 1 else "square,pad=0",
                linewidth=0,
                facecolor=color
            ))

    # Cores do gradiente (AZUL ESCURO → CIANO CLARO)
    cor_escura = (13, 42, 82)    # #0D2A52
    cor_clara = (61, 174, 233)   # #3DAEE9 (ciano elegante)

    # === Renderização ===
    for i, (_, row) in enumerate(df_top.iterrows()):
        y = y_start - i * y_gap

        empresa = row["EMPRESA"]
        pct = float(row["Impacto_Pct"])

        # Nome da concessionária
        ax.text(0.02, y, empresa,
                fontsize=16, fontweight="bold",
                ha="left", va="center")

        # Barra
        barra_x = 0.20
        barra_y = y - barra_altura/2
        barra_total = 0.45
        barra_w = barra_total * row["Largura"]

        # Barra com gradiente REAL
        gradiente(ax, barra_x, barra_y, barra_w, barra_altura, cor_escura, cor_clara)

        # Percentual centralizado dentro da barra
        ax.text(
            barra_x + barra_w/2,
            barra_y + barra_altura/2,
            f"{pct:.2f}%".replace(".", ","),
            fontsize=14,
            fontweight="bold",
            color="white",
            ha="center", va="center"
        )

    plt.tight_layout()
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close()

    return caminho





def gerar_imagens_top3_de_top10(df_mes, top10_df, pasta_saida):
    """
    Função principal que orquestra:
    - extrai top3 concessionarias por serviço (considerando agrupar serviços no df_mes)
    - gera 1 imagem por cada um dos 3 serviços do top10_df
    Retorna lista de caminhos gerados.
    """
    resultados = extrair_top3_concessionarias_por_servico(df_mes, top10_df, n=3)
    caminhos = []
    for servico, info in resultados.items():
        caminho = gerar_imagem_impacto(servico, info, pasta_saida)
        caminhos.append(caminho)
    return caminhos
