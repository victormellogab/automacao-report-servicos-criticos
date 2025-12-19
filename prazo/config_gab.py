import os

# Caminhos dos arquivos
CAMINHO_INOVA = r"C:\dados-report\base_report_novembro.xlsx"
CAMINHO_SERVICOS = r"C:\dados-report\TODOS_SERVICOS.csv"

# Pasta de saída
PASTA_SAIDA = r'H:\COMERCIAL\MEDIÇÃO\ARQUIVO MORTO\BERNARDO\GSC\Automação Report'
os.makedirs(PASTA_SAIDA, exist_ok=True)

# Lista de concessionárias
CONCESSIONARIAS = [
    'CAAN',
    'CAC',
    'CAI',
    'CAIZ',
    'CAJ',
    'CAJA',
    'CAN',
    'CANF',
    'CAP',
    'CAPAM',
    'CAPY',
    'CAV',
    #'RIOMAIS'
]
