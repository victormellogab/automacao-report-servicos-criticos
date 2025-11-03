import plotly.graph_objects as go

def gerar_cards_os(df_mes, conc, caminho_arquivo):
    # Cálculos
    total_os = len(df_mes)
    no_prazo = len(df_mes[df_mes['StatusPrazo'] == 'No Prazo'])
    fora_prazo = len(df_mes[df_mes['StatusPrazo'] == 'Fora do Prazo'])

    pct_no = round((no_prazo / total_os) * 100, 2) if total_os > 0 else 0
    pct_fora = round((fora_prazo / total_os) * 100, 2) if total_os > 0 else 0
    total_os_fmt = f"{total_os:,}".replace(",", ".")

    # Cores e textos
    cores = ["#001f4d", "#2e7d32", "#f57c00"]
    textos = [("Qtde Serviços", total_os_fmt),
              ("Serviços no Prazo", f"{pct_no:.2f}%"),
              ("Serviços Fora do Prazo", f"{pct_fora:.2f}%")]

    fig = go.Figure()

    # Tamanho dos cards
    card_width = 0.8
    card_height = 1
    card_gap = 0.07
    radius = 0.15

    # Função para retângulo arredondado
    def rounded_rect(x0, y0, x1, y1, r):
        return f'M {x0+r},{y0} ' \
               f'L {x1-r},{y0} Q {x1},{y0} {x1},{y0+r} ' \
               f'L {x1},{y1-r} Q {x1},{y1} {x1-r},{y1} ' \
               f'L {x0+r},{y1} Q {x0},{y1} {x0},{y1-r} ' \
               f'L {x0},{y0+r} Q {x0},{y0} {x0+r},{y0} Z'

    for i, (label, valor) in enumerate(textos):
        x0 = i * (card_width + card_gap)
        x1 = x0 + card_width
        y0 = 0
        y1 = card_height

        # Card arredondado
        fig.add_shape(
            type="path",
            path=rounded_rect(x0, y0, x1, y1, radius),
            fillcolor=cores[i],
            line=dict(width=0)
        )

        # Valor centralizado
        fig.add_annotation(
            x=(x0+x1)/2,
            y=y0 + card_height*0.56,  # posição do valor
            text=f"<b>{valor}</b>",
            showarrow=False,
            font=dict(color="white", size=42),
            xanchor="center",
            yanchor="middle"
        )

        # Label logo abaixo do valor em negrito
        fig.add_annotation(
            x=(x0+x1)/2,
            y=y0 + card_height*0.36,  # um espacinho abaixo
            text=f"<b>{label}</b>",   # negrito
            showarrow=False,
            font=dict(color="white", size=20),
            xanchor="center",
            yanchor="middle"
        )

    # Ajustar layout para remover todo espaço extra
    fig.update_xaxes(visible=False, range=[0, len(textos)*(card_width+card_gap)-card_gap])
    fig.update_yaxes(visible=False, range=[0, card_height])
    fig.update_layout(
        width=int(len(textos)*(card_width*480)),  # reduzir largura total proporcional
        height=230,  # aumenta um pouco a altura para deixar menos retangular
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    fig.write_image(f"{caminho_arquivo}.png", scale=3)
