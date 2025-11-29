import plotly.graph_objects as go
import math

def salvar_tabela_top3_compacto_tempo(df, caminho_arquivo):

    df2 = df.copy()

    # Mapear colunas (TEMPO)
    df2["Serviços"] = df2[df.columns[0]]            # Servico_Limpo
    df2["Qtde de OS (Geral)"] = df2[df.columns[1]]  # Qtde_OS

    # ===== CALCULAR QTD OS NO TEMPO (igual ao DAX) =====
    df2["Qtde de OS (No Tempo)"] = (df2[df.columns[5]] / 100) * df2[df.columns[1]]
    df2["Qtde de OS (No Tempo)"] = df2["Qtde de OS (No Tempo)"].round(0).astype(int)

    df2["% Serviços no Tempo"] = df2[df.columns[5]]     # %_No_Tempo

    # -------- FORMATAR ----------
    df2["Qtde de OS (Geral)"] = df2["Qtde de OS (Geral)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df2["Qtde de OS (No Tempo)"] = df2["Qtde de OS (No Tempo)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df2["% Serviços no Tempo"] = df2["% Serviços no Tempo"].apply(lambda x: f"{x:.2f}".replace(".", ","))

    # -------- CORES (%) ----------
    cores_pct = []
    for val in df[df.columns[5]]:
        if val < 60:
            cores_pct.append("#FFBFC4")  # vermelho claro
        elif val < 85:
            cores_pct.append("#FFEC6E")  # amarelo claro
        else:
            cores_pct.append("#A6DFB4")  # verde claro

    altura_header = 40
    altura_base = 38
    chars_por_linha = 28

    max_linhas = max(math.ceil(len(texto) / chars_por_linha) for texto in df2["Serviços"])
    altura_linha_final = altura_base * max(1, max_linhas)

    altura_total = altura_header + len(df2) * altura_linha_final + 20

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Serviços",
                        "Qtde de OS (Geral)",
                        "Qtde de OS (No Tempo)",
                        "% Serviços no Tempo"
                    ],
                    fill_color="#002060",
                    font=dict(color="white", size=18, family="Arial"),
                    align="center",
                    height=altura_header,
                    line_color="black",
                    line_width=2
                ),
                cells=dict(
                    values=[
                        df2["Serviços"],
                        df2["Qtde de OS (Geral)"],
                        df2["Qtde de OS (No Tempo)"],
                        df2["% Serviços no Tempo"],
                    ],
                    fill_color=[
                        ['white'] * len(df2),
                        ['white'] * len(df2),
                        ['white'] * len(df2),
                        cores_pct
                    ],
                    align="center",
                    font=dict(color="black", size=16, family="Arial"),
                    height=altura_linha_final,   # altura única e válida
                    line_color="black",
                    line_width=1
                ),
                columnwidth=[0.15, 0.09, 0.09, 0.09]  # igual ao prazo
            )
        ]
    )

    fig.update_layout(
        autosize=False,
        width=600,
        height=altura_total,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    fig.write_image(f"{caminho_arquivo}.png")
