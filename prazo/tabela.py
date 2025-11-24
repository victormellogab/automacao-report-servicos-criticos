import plotly.graph_objects as go

def salvar_tabela_img(df, caminho_arquivo):
    # Renomear colunas
    df = df.rename(columns={
        df.columns[0]: "Serviços",
        df.columns[1]: "Qtde de OS (Geral)",
        df.columns[2]: "Prazo Padrão (Dias)",
        df.columns[3]: "Média Execução (Dias)",
        df.columns[4]: "Diferença (Dias)",
        df.columns[5]: "% OS no Prazo Padrão"
    })

    # Formatar dados
    df_format = df.copy()
    df_format["Qtde de OS (Geral)"] = df_format["Qtde de OS (Geral)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    for col in ["Prazo Padrão (Dias)", "Média Execução (Dias)", "Diferença (Dias)"]:
        df_format[col] = df_format[col].apply(lambda x: f"{x:.2f}".replace(".", ","))
    df_format["% OS no Prazo Padrão"] = df_format["% OS no Prazo Padrão"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

    # Cores Diferença
    cores_diferenca = []
    for val in df[df.columns[4]]:
        if val > 0:
            cores_diferenca.append("#FFBFC4")  # vermelho claro
        elif val < 0:
            cores_diferenca.append("#A6DFB4")  # verde claro
        else:
            cores_diferenca.append("white")

    # Cores % OS no Prazo Padrão
    cores_prazo = []
    for val in df[df.columns[5]]:  # valores de 0 a 100
        if val < 60:          # até 59,99%
            cores_prazo.append("#FFBFC4")  # vermelho claro
        elif val < 85:        # 60 até 84,99%
            cores_prazo.append("#FFEC6E")  # laranja claro
        else:                 # 85% ou mais
            cores_prazo.append("#A6DFB4")  # verde claro

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
                        cores_prazo                 
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

def salvar_tabela_top10_expandido_img(df, caminho_arquivo):

    df_format = df.copy()

    # ======================
    # Empilhar quantidade
    # ======================
    qtde_col = []
    for _, row in df.iterrows():
        if row["Tipo"] == "SERVICO":
            qtde_col.append(f"{row['Qtde_OS']}")
        else:
            qtde_col.append(f"{row['Qtde_OS']}")
    df_format["Qtde_OS_final"] = qtde_col

    # ======================
    # Serviço aparece só na linha principal
    # ======================
    df_format["Servico_Final"] = [
        row["Servico"] if row["Tipo"] == "SERVICO" else row["Empresa"]
        for _, row in df_format.iterrows()
    ]

    # ======================
    # Formatação final
    # ======================
    df_format["Prazo_Padrão"] = df_format["Prazo_Padrao"].apply(lambda x: f"{x:.2f}".replace(".", ",") if x != "" else "")
    df_format["Média_Execução"] = df_format["Media_Execucao"].apply(lambda x: f"{x:.2f}".replace(".", ",") if x != "" else "")
    df_format["Diferença"] = df_format["Diferença"].apply(lambda x: f"{x:.2f}".replace(".", ",") if x != "" else "")
    df_format["% No Prazo"] = df_format["%_No_Prazo"].apply(lambda x: f"{x:.2f}%".replace(".", ",") if x != "" else "")
    df_format["Impacto"] = df_format["Impacto"].apply(lambda x: f"{x:.2f}%".replace(".", ",") if x != "" else "")

    # ======================
    # Fundo das linhas (SERVIÇO vs EMPRESA)
    # ======================
    cores_linha = [
        "#E8E8E8" if row["Tipo"] == "SERVICO" else "white"
        for _, row in df_format.iterrows()
    ]

    # ======================
    # Cores Diferença (apenas linha SERVIÇO)
    # ======================
    cores_diferenca = []
    for _, row in df_format.iterrows():
        if row["Tipo"] != "SERVICO":
            cores_diferenca.append("white")
        else:
            if row["Diferença"] == "":
                cores_diferenca.append("white")
            else:
                n = float(row["Diferença"].replace(",", "."))
                if n > 0:
                    cores_diferenca.append("#FFBFC4")
                elif n < 0:
                    cores_diferenca.append("#A6DFB4")
                else:
                    cores_diferenca.append("white")

    # ======================
    # Cores % No Prazo (linha serviço)
    # ======================
    cores_prazo = []
    for _, row in df_format.iterrows():
        val = row["% No Prazo"]
        if row["Tipo"] != "SERVICO" or val == "":
            cores_prazo.append("white")
        else:
            n = float(val.replace("%", "").replace(",", "."))
            if n < 60:
                cores_prazo.append("#FFBFC4")
            elif n < 85:
                cores_prazo.append("#FFEC6E")
            else:
                cores_prazo.append("#A6DFB4")

    # ======================
    # Construir tabela
    # ======================
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Serviço",
                        "Qtde de OS (Geral)",
                        "Prazo Padrão (Dias)",
                        "Média Execução (Dias)",
                        "Diferença (Dias)",
                        "% OS no Prazo",
                        "Impacto (%)"
                    ],
                    fill_color="#002060",
                    font=dict(color="white", size=20),
                    align="center",
                    height=44,
                    line_color="black",
                    line_width=2
                ),
                cells=dict(
                    values=[
                        df_format["Servico_Final"],
                        df_format["Qtde_OS_final"],
                        df_format["Prazo_Padrão"],
                        df_format["Média_Execução"],
                        df_format["Diferença"],
                        df_format["% No Prazo"],
                        df_format["Impacto"],
                    ],
                    fill_color=[
                        cores_linha,
                        cores_linha,
                        cores_linha,
                        cores_linha,
                        cores_diferenca,   # mantém coloração
                        cores_prazo,       # mantém coloração
                        cores_linha
                    ],
                    align="center",
                    font=dict(color="black", size=18),
                    height=40,
                    line_color="black",
                    line_width=1
                )
            )
        ]
    )

    # ======================
    # Altura automática (sem cortes)
    # ======================
    altura = len(df_format) * 60

    fig.update_layout(
        autosize=False,
        width=1500,
        height=altura,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    fig.write_image(f"{caminho_arquivo}.png", scale=3)

'''def salvar_tabela_img_grupo(df, caminho_arquivo):
    """
    Salva tabela do TOP 10 por grupo no mesmo layout da tabela original.
    """

    df = df.rename(columns={
        df.columns[0]: "Grupo de Serviços",
        df.columns[1]: "Qtde de OS (Geral)",
        df.columns[2]: "Prazo Padrão (Dias)",
        df.columns[3]: "Média Execução (Dias)",
        df.columns[4]: "Diferença (Dias)",
        df.columns[5]: "% OS no Prazo Padrão"
    })

    df_format = df.copy()

    # Formatação
    df_format["Qtde de OS (Geral)"] = df_format["Qtde de OS (Geral)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    for col in ["Prazo Padrão (Dias)", "Média Execução (Dias)", "Diferença (Dias)"]:
        df_format[col] = df_format[col].apply(lambda x: f"{x:.2f}".replace(".", ","))

    df_format["% OS no Prazo Padrão"] = df_format["% OS no Prazo Padrão"].apply(
        lambda x: f"{x:.2f}%".replace(".", ",")
    )

    # Cores dif e % (igual tabela original)
    cores_diferenca = [
        "#FFBFC4" if val > 0 else ("#A6DFB4" if val < 0 else "white")
        for val in df["Diferença (Dias)"]
    ]

    cores_prazo = []
    for val in df["% OS no Prazo Padrão"]:
        if val < 60:
            cores_prazo.append("#FFBFC4")
        elif val < 85:
            cores_prazo.append("#FFEC6E")
        else:
            cores_prazo.append("#A6DFB4")

    fig = go.Figure(
        data=[go.Table(
            header=dict(
                values=list(df_format.columns),
                fill_color="#002060",
                align="center",
                font=dict(color="white", size=20, family="Arial"),
                height=44
            ),
            cells=dict(
                values=[df_format[c] for c in df_format.columns],
                fill_color=[
                    ['white']*len(df_format),
                    ['white']*len(df_format),
                    ['white']*len(df_format),
                    ['white']*len(df_format),
                    cores_diferenca,
                    cores_prazo
                ],
                align="center",
                font=dict(color="black", size=18, family="Arial"),
                height=40
            )
        )]
    )

    fig.update_layout(
        width=1500,
        height=44 + len(df_format)*40 + 20,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white"
    )

    fig.write_image(f"{caminho_arquivo}.png", scale=3)
'''