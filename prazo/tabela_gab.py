import plotly.graph_objects as go
import math

def salvar_tabela_top3_compacto(df, caminho_arquivo):

    df2 = df.copy()

    # Mapear colunas
    df2["Serviços"] = df2[df.columns[0]]
    df2["Qtde de OS (Geral)"] = df2[df.columns[1]]

    # Calcular Qtd de OS no prazo (igual ao DAX)
    df2["Qtde de OS (No Prazo)"] = (df2[df.columns[5]] / 100) * df2[df.columns[1]]
    df2["Qtde de OS (No Prazo)"] = df2["Qtde de OS (No Prazo)"].round(0).astype(int)

    df2["% Serviços no Prazo"] = df2[df.columns[5]]

    # Formatação
    df2["Qtde de OS (Geral)"] = df2["Qtde de OS (Geral)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df2["Qtde de OS (No Prazo)"] = df2["Qtde de OS (No Prazo)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df2["% Serviços no Prazo"] = df2["% Serviços no Prazo"].apply(lambda x: f"{x:.2f}".replace(".", ","))

    # Cores
    cores_pct = []
    for val in df[df.columns[5]]:
        if val < 60:
            cores_pct.append("#FFBFC4")
        elif val < 85:
            cores_pct.append("#FFEC6E")
        else:
            cores_pct.append("#A6DFB4")

    # ALTURA LINHAS
    altura_header = 40
    altura_base = 38
    chars_por_linha = 28
    max_linhas = max(math.ceil(len(texto) / chars_por_linha) for texto in df2["Serviços"])
    altura_linha_final = altura_base * max(1, max_linhas)
    altura_total = altura_header + len(df2) * altura_linha_final + 20

    # MONTAR TABELA
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Serviços",
                        "Qtde de OS (Geral)",
                        "Qtde de OS (No Prazo)",
                        "% Serviços no Prazo"
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
                        df2["Qtde de OS (No Prazo)"],
                        df2["% Serviços no Prazo"],
                    ],
                    fill_color=[
                        ['white'] * len(df2),
                        ['white'] * len(df2),
                        ['white'] * len(df2),
                        cores_pct
                    ],
                    align="center",
                    font=dict(color="black", size=16, family="Arial"),
                    height=altura_linha_final,
                    line_color="black",
                    line_width=1
                ),
                columnwidth=[0.15, 0.09, 0.09, 0.09]
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
