import os
import win32com.client

PASTA_DOCX = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Report\dezembro"
PASTA_PDF = os.path.join(PASTA_DOCX, "pdf")

os.makedirs(PASTA_PDF, exist_ok=True)

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

try:
    for arquivo in os.listdir(PASTA_DOCX):
        if arquivo.lower().endswith(".docx"):
            caminho_docx = os.path.join(PASTA_DOCX, arquivo)
            nome_pdf = os.path.splitext(arquivo)[0] + ".pdf"
            caminho_pdf = os.path.join(PASTA_PDF, nome_pdf)

            doc = word.Documents.Open(caminho_docx)

            doc.ExportAsFixedFormat(
                OutputFileName=caminho_pdf,
                ExportFormat=17,          # PDF
                OpenAfterExport=False,
                OptimizeFor=0,            # 0 = impressão (MÁXIMA QUALIDADE)
                CreateBookmarks=1,        # mantém estrutura
                DocStructureTags=True,
                BitmapMissingFonts=True,
                UseISO19005_1=False
            )

            doc.Close(False)
            print(f"Convertido (alta qualidade): {arquivo}")

finally:
    word.Quit()

print("✅ Conversão finalizada em ALTA QUALIDADE.")
