documentação rápida:

para funcionar a automação para as Concessionárias, a ordem para rodar será:

1º - exportar a base da data que quer do BI do Report
2º - configurar o intervalo de datas e caminho do arquivo dessa base
3º - rodar primeiro prazo/gerar_imagens (vai gerar o card, tabelas e gráfico da primeira página de prazo)
4º - rodar depois tempo/gerar_imagens (vai gerar o card, tabelas e gráfico da segunda página de tempo)
5º - só assim rodar ./main.py (o da raiz do projeto, que vai consolidar as imagens geradas e construir o report em .docx)



para funcionar a automação para o GAB, a ordem para rodar será:
1º - com as concessionárias já geradas e o período ajustado, rodar:
1.1º - prazo/gab_gerar_imagens.py
1.2º - tempo/gab_gerar_imagens.py

obs: atualmente o código GAB não está finalizado para anexar as imagens nesse novo padrão no documento. então depois de rodar eles, será necessário anexar as imagens manualmente.



ajustar: consolidar as informações mutáveis na raiz, para facilitar o ajuste.
