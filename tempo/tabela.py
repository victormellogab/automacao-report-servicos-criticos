import plotly.graph_objects as go

def salvar_tabela_img(df, caminho_arquivo):

    # Renomear colunas
    df = df.rename(columns={
        df.columns[0]: "Serviços",
        df.columns[1]: "Qtde de OS (Geral)",
        df.columns[2]: "Tempo Padrão (Minutos)",
        df.columns[3]: "Média Execução (Minutos)",
        df.columns[4]: "Diferença (Minutos)",
        df.columns[5]: "% OS no Tempo Padrão"
    })

    # Formatar dados
    df_format = df.copy()

    df_format["Qtde de OS (Geral)"] = df_format["Qtde de OS (Geral)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    for col in ["Tempo Padrão (Minutos)", "Média Execução (Minutos)", "Diferença (Minutos)"]:
        df_format[col] = df_format[col].apply(lambda x: f"{x:.2f}".replace(".", ","))

    df_format["% OS no Tempo Padrão"] = df_format["% OS no Tempo Padrão"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

    # Cores Diferença
    cores_diferenca = []
    for val in df[df.columns[4]]:
        if val > 0:
            cores_diferenca.append("#FFBFC4")  # vermelho
        elif val < 0:
            cores_diferenca.append("#A6DFB4")  # verde
        else:
            cores_diferenca.append("white")

    # Cores % no tempo padrão
    cores_tempo = []
    for val in df[df.columns[5]]:
        if val < 60:
            cores_tempo.append("#FFBFC4")
        elif val < 85:
            cores_tempo.append("#FFEC6E")
        else:
            cores_tempo.append("#A6DFB4")

    # Criar tabela
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(df_format.columns),
                    fill_color="#002060",
                    align="center",
                    font=dict(color="white", size=20, family="Arial"),
                    height=44,
                    line_color="black",
                    line_width=2
                ),
                cells=dict(
                    values=[df_format[c] for c in df_format.columns],
                    fill_color=[
                        ['white']*len(df_format),
                        ['white']*len(df_format),
                        ['white']*len(df_format),
                        ['white']*len(df_format),
                        cores_diferenca,
                        cores_tempo
                    ],
                    align="center",
                    font=dict(color="black", size=18, family="Arial"),
                    height=40,
                    line_color="black",
                    line_width=1
                ),
                columnwidth=[0.3, 0.07, 0.08, 0.09, 0.06, 0.08]
            )
        ]
    )

    linhas = len(df_format)
    altura = 44 + linhas*40 + 20
    largura = 1500

    fig.update_layout(
        autosize=False,
        width=largura,
        height=altura,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    fig.write_image(f"{caminho_arquivo}.png", scale=3)

def salvar_tabela_top10_expandido_img_tempo(df, caminho_arquivo):

    df_format = df.copy()

    # Empilhar quantidade
    qtde_col = []
    for _, row in df.iterrows():
        if row["Tipo"] == "SERVICO":
            qtde_col.append(f"{row['Qtde_OS']}")
        else:
            qtde_col.append(f"{row['Qtde_OS']}")
    df_format["Qtde_OS_final"] = qtde_col

    # Serviço/empresa
    df_format["Servico_Final"] = [
        row["Servico"] if row["Tipo"] == "SERVICO" else row["Empresa"]
        for _, row in df_format.iterrows()
    ]

    # Formatação
    df_format["Tempo_Padrão"] = df_format["TempoPadrao"].apply(
        lambda x: f"{x:.2f}".replace(".", ",") if x != "" else ""
    )
    df_format["Média_Execução"] = df_format["Media_Execucao"].apply(
        lambda x: f"{x:.2f}".replace(".", ",") if x != "" else ""
    )
    df_format["Diferença"] = df_format["Diferença"].apply(
        lambda x: f"{x:.2f}".replace(".", ",") if x != "" else ""
    )
    df_format["% No Tempo"] = df_format["%_No_Tempo"].apply(
        lambda x: f"{x:.2f}%".replace(".", ",") if x != "" else ""
    )
    df_format["Impacto"] = df_format["Impacto"].apply(
        lambda x: f"{x:.2f}%".replace(".", ",") if x != "" else ""
    )

    # fundo das linhas
    cores_linha = [
        "#E8E8E8" if row["Tipo"] == "SERVICO" else "white"
        for _, row in df_format.iterrows()
    ]

    # cores de diferença
    cores_diferenca = []
    for _, row in df_format.iterrows():
        if row["Tipo"] != "SERVICO":
            cores_diferenca.append("white")
        else:
            val = row["Diferença"]
            if val == "":
                cores_diferenca.append("white")
            else:
                n = float(val.replace(",", "."))
                if n > 0:
                    cores_diferenca.append("#FFBFC4")
                elif n < 0:
                    cores_diferenca.append("#A6DFB4")
                else:
                    cores_diferenca.append("white")

    # cores % no tempo
    cores_tempo = []
    for _, row in df_format.iterrows():
        val = row["% No Tempo"]
        if row["Tipo"] != "SERVICO" or val == "":
            cores_tempo.append("white")
        else:
            n = float(val.replace("%", "").replace(",", "."))
            if n < 60:
                cores_tempo.append("#FFBFC4")
            elif n < 85:
                cores_tempo.append("#FFEC6E")
            else:
                cores_tempo.append("#A6DFB4")

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Serviço",
                        "Qtde de OS (Geral)",
                        "Tempo Padrão (Min)",
                        "Média Execução (Min)",
                        "Diferença (Min)",
                        "% OS no Tempo",
                        "Impacto (%)"
                    ],
                    fill_color="#002060",
                    font=dict(color="white", size=20),
                    align="center",
                    height=44,
                    line_color="black",     # << ADICIONADO
                    line_width=2            # << ADICIONADO
                ),
                cells=dict(
                    values=[
                        df_format["Servico_Final"],
                        df_format["Qtde_OS_final"],
                        df_format["Tempo_Padrão"],
                        df_format["Média_Execução"],
                        df_format["Diferença"],
                        df_format["% No Tempo"],
                        df_format["Impacto"],
                    ],
                    fill_color=[
                        cores_linha,
                        cores_linha,
                        cores_linha,
                        cores_linha,
                        cores_diferenca,
                        cores_tempo,
                        cores_linha
                    ],
                    align="center",
                    font=dict(color="black", size=18),
                    height=40,
                    line_color="black",     # << ADICIONADO
                    line_width=1            # << ADICIONADO
                )
            )
        ]
    )

    fig.update_layout(
        autosize=False,
        width=1500,
        height=len(df_format)*60,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    fig.write_image(f"{caminho_arquivo}.png", scale=3)
