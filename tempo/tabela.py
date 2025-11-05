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
