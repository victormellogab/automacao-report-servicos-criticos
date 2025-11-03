import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# ----------- CONFIGURAÇÃO -----------
PASTA_SAIDA = r'H:\COMERCIAL\MEDIÇÃO\ARQUIVO MORTO\BERNARDO\GSC\Automação Report'
os.makedirs(PASTA_SAIDA, exist_ok=True)

CONCESSIONARIAS = [
    'CAC',
]

CONCESSIONARIA_NOME = {
    'CAC': 'Concessionária Águas das Agulhas Negras',
}

MES = "Outubro"
ANO = 2025

IMAGENS = {
    'CAC': {
        "card_prazo": os.path.join(PASTA_SAIDA, "CAC_Resumo_Setembro.png"),
        "top10_prazo": os.path.join(PASTA_SAIDA, "CAC_Top10_Setembro.png"),
        "top3_prazo": os.path.join(PASTA_SAIDA, "CAC_Top3_3Meses.png"),
        "grafico_prazo": os.path.join(PASTA_SAIDA, "CAC_Evolucao_Abr-Set_2025.png"),
        "card_tempo": None,
        "top10_tempo": None,
        "top3_tempo": None,
        "grafico_tempo": None,
        "tabela_prioritarios": None
    }
}

def add_imagem_ou_texto(doc, texto, caminho_imagem, tamanho_pct=100):
    p = doc.add_paragraph()
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    if caminho_imagem:
        # calcula a largura em polegadas proporcional ao percentual
        largura_inch = Inches(6) * (tamanho_pct / 100)
        run = p.add_run()
        run.add_picture(caminho_imagem, width=largura_inch)
    else:
        run = p.add_run(texto)
        run.font.name = "Calibri"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
        run.font.size = Pt(12)
        run.font.bold = False
        run.font.color.rgb = RGBColor(0,0,0)

# ----------- FUNÇÃO DE CRIAÇÃO DO DOCX COM IMAGENS E FONTE PADRÃO -----------
def gerar_documento_report(concessionaria, pasta_saida, imagens):
    doc = Document()

    # ---------- CONFIGURAR MARGENS ----------
    section = doc.sections[0]
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)

    # ---------- CONFIGURAR FONTE PADRÃO ----------
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')

    # Configurar estilos de títulos para Calibri também
    for level in range(1, 10):
        try:
            s = doc.styles[f'Heading {level}']
            s.font.name = 'Calibri'
            s.font.size = Pt(12)
            s.font.bold = False
            s.font.color.rgb = RGBColor(0,0,0)
            s.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
        except KeyError:
            pass

    # Nome completo da concessionária
    nome_conc = CONCESSIONARIA_NOME.get(concessionaria, concessionaria)

    # Título
    p = doc.add_paragraph()
    run = p.add_run(nome_conc)
    run.font.name = 'Calibri'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
    run.font.size = Pt(21)

    # << SHIFT+ENTER >>
    run.add_break()  # quebra de linha sem espaço extra

    # Subtítulo na mesma estrutura
    run2 = p.add_run(f"Report Cesta de Serviços – {MES} {ANO}")
    run2.font.name = 'Calibri'
    run2._element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
    run2.font.size = Pt(12)

    # Prazo padrão
    h = doc.add_heading("Indicador de Serviços no Prazo Padrão", level=1)
    h.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    add_imagem_ou_texto(doc, "[Imagem do card em anexo]", imagens["card_prazo"], tamanho_pct=70)

    # Top 10
    h = doc.add_heading("Top 10 Serviços com Menor Percentual de OS no Prazo Padrão", level=1)
    h.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    add_imagem_ou_texto(doc, "[Imagem da tabela top10 em anexo]", imagens["top10_prazo"], tamanho_pct=115)

    # Top 3
    h = doc.add_heading("Top 3 Percentis de Desempenho – Maiores Ofensores (Ref. Últimos 3 meses)", level=1)
    h.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    add_imagem_ou_texto(doc, "[Imagem da tabela top3 em anexo]", imagens["top3_prazo"], tamanho_pct=110)

    # Gráfico
    h = doc.add_heading("Qtde de OS e % Serviços no Prazo - Últimos 6 meses", level=1)
    h.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    add_imagem_ou_texto(doc, "[Imagem do gráfico em anexo]", imagens["grafico_prazo"], tamanho_pct=80)

    # ANEXO
    doc.add_heading("ANEXO", level=1)
    doc.add_paragraph("Considera-se essa Tabela de Serviços Prioritários:")
    doc.add_paragraph("[Imagem da tabela de serviços em anexo]")

    # Fonte de dados e premissas
    doc.add_heading("FONTE DE DADOS", level=1)
    doc.add_paragraph(
        "Todos os dados utilizados neste painel são provenientes da seguinte base:\n"
        "• Inova: Informações de serviços, ordens de serviço, prazo padrão e tempo padrão."
    )

    doc.add_heading("REGRAS E PREMISSAS", level=1)
    doc.add_paragraph(
        "O que foi considerado:\n"
        "• Exclusão da área de Engenharia\n"
        "• Considera o Dia do Prazo + 3 dias para os serviços do GSC que possuem apropriação manual\n"
        "• Tempo de Execução: Diferença entre início e fim da execução do serviço\n"
        "• Dias de Execução: Diferença entre Data Inclusão e Data Baixa do serviço\n"
        "• Remoção de serviços executados sem tempo de início e fim de execução"
    )

    # Salvar documento
    caminho_doc = os.path.join(pasta_saida, f"{concessionaria}_Report.docx")
    doc.save(caminho_doc)
    print(f"Documento gerado: {caminho_doc}")


# ----------- EXECUÇÃO -----------
if __name__ == "__main__":
    for conc in CONCESSIONARIAS:
        gerar_documento_report(conc, PASTA_SAIDA, IMAGENS[conc])
