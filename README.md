# Documentação Rápida

## Automação para Concessionárias

Para que a automação funcione corretamente para as **Concessionárias**, a ordem de execução deve ser **exatamente** a seguinte:

1. **Exportar a base** da data desejada a partir do BI (Report).
2. **Configurar o intervalo de datas** e o **caminho do arquivo** dessa base exportada.
3. **Executar**:
   ```bash
   prazo/gerar_imagens.py
   ```
>
4. **Executar**:
  ```bash
  tempo/gerar_imagens.py
  ```
>
5. **Executar**
  ```bash
  ./main.py
  ```
>


## Automação para GAB

PAra que a automação funcione corretamente para todas as **Concessionárias**, a ordem de execução deve ser **exatamente** a seguinte:

1. **Exportar a base** da data desejada a partir do BI (Report). Vale lembrar que se fez o procedimento para rodar o das concessionárias de forma separada, a base ainda seria a mesma. Entao não precisa puxar de novo.

2. **Configurar o inter alo de datas** e o **caminho do arquivo** dessa base exportada. Vale lembrar que se fez o procedimento para roda o das concessionária de forma separada, a base ainda seria a mesma. Então não precisa puxar de novo.

3. **Executar**:
> Com as concessionárias já geradas e o perído ajustado:
  ```bash
  	prazo/gab_gerar_imagens.py
  ```
  e

  ```bash
  tempo/gab_gerar_imagens.py
  ```
