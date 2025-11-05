import os

# Caminhos dos arquivos
CAMINHO_INOVA = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Script Geração Report Serviços\Dados\data.csv"
CAMINHO_SERVICOS = r"C:\Users\victor.mello\OneDrive - Grupo Aguas do Brasil\Área de Trabalho\Script Geração Report Serviços\Dados\TODOS_SERVICOS.csv"

# Pasta de saída
PASTA_SAIDA = r'H:\COMERCIAL\MEDIÇÃO\ARQUIVO MORTO\BERNARDO\GSC\Automação Report'
os.makedirs(PASTA_SAIDA, exist_ok=True)

# Lista de concessionárias
CONCESSIONARIAS = [
    #'CAAN',
    'CAC',
    #'CAI',
    #'CAIZ',
    #'CAJ',
    #'CAJA',
    #'CAN',
    #'CANF',
    #'CAP',
    #'CAPAM',
    #'CAPY',
    #'CAV',
    #'RIOMAIS'
]
