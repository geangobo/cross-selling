# 🛒 Análise de Cesta (Market Basket Analysis) com Polars e FP-Growth

## 🎯 Objetivo do Projeto

Este projeto realiza uma Análise de Cesta de Compras utilizando dados transacionais (itens de notas fiscais), com manipulação de dados performática via Polars e mineração de itemsets frequentes usando o algoritmo FP-Growth. O objetivo principal é identificar regras de associação do tipo "SE compra Produto X, ENTÃO compra Produto Y", descobrindo quais produtos são frequentemente comprados juntos e a força dessas associações para insights de negócio.

## 🛠️ Tecnologias Utilizadas

* **Python 3.9.13** (ou a versão que estiver usando)
* **Polars:** Para manipulação e preparação de dados de alta performance.
* **Mlxtend:** Para implementação do algoritmo FP-Growth e geração das regras de associação.
* Matplotlib & Seaborn: Para visualização de dados (gráficos de barras, dispersão, heatmaps).
* NetworkX: Para criação e visualização do grafo de associação de produtos (se utilizado).
* Pandas: Utilizado pontualmente para interface com `mlxtend` e agrupamento específico.
* Openpyxl: Para exportar os resultados para formato Excel (.xlsx) (ou `xlsxwriter`).

## ⚙️ Configuração e Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_AQUI]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```
2.  **(Recomendado) Crie um Ambiente Virtual:**
    ```bash
    python -m venv venv
    # No Windows:
    venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    Certifique-se de ter um arquivo `requirements.txt` no seu projeto que inclua `polars`, `mlxtend`, `matplotlib`, `seaborn`, `networkx`, `pandas`, `openpyxl` (ou `xlsxwriter`), etc. Se não tiver, você pode gerá-lo com `pip freeze > requirements.txt`.
    Para instalar os pacotes necessários, execute:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Execução da Análise

1.  **Dados de Entrada:** Coloque os arquivos de dados Olist (ou outro) na pasta `/data/` (ou conforme configurado no script/notebook).
2.  **Execute o Script/Notebook:** Execute o arquivo Python principal (ex: `analise_cesta_olist.py`) ou as células do Jupyter Notebook (`src/`). O código utiliza Polars para pré-processamento, Pandas para um passo de agrupamento específico, e `mlxtend` com **FP-Growth** para a análise de cesta.
3.  **Resultados:** O processo irá gerar:
    * Logs de execução no console/notebook.
    * Visualizações (se incluídas no código para execução direta).
    * Um arquivo Excel (ex: `regras_fpgrowth_olist_final.xlsx`) contendo a tabela final com as regras de associação, métricas e categorias/nomes dos produtos.

## 💡 Conceitos Chave

* **Análise de Cesta (Market Basket Analysis):** 🧺 É uma técnica de mineração de dados usada para descobrir associações entre itens frequentemente comprados juntos. Ajuda a entender o comportamento de compra e embasar decisões de marketing, layout e recomendação.

* **Algoritmo FP-Growth:** 🌳 Escolhido para este projeto por sua eficiência e robustez em encontrar "itemsets frequentes" (conjuntos de itens que aparecem juntos acima de um `min_support`). Diferente do Apriori, o FP-Growth:
    1.  **Evita Geração de Candidatos:** Não precisa gerar e testar um número potencialmente enorme de combinações de itens intermediários, que é um gargalo do Apriori.
    2.  **Usa a FP-Tree:** Constrói uma estrutura de dados em árvore compacta (FP-Tree) que armazena os padrões frequentes com apenas duas varreduras nos dados.
    3.  **Minera a Árvore:** Extrai os itemsets frequentes diretamente da FP-Tree, geralmente resultando em melhor desempenho (velocidade e uso de memória), especialmente em datasets maiores ou mais densos.

* **Biblioteca `mlxtend`:** 🐍 É uma biblioteca Python essencial para esta análise, fornecendo as implementações:
    * **`mlxtend.frequent_patterns.fpgrowth`:** Função utilizada neste projeto para encontrar os itemsets frequentes de forma eficiente.
    * `mlxtend.frequent_patterns.association_rules`: Função usada para gerar as regras de associação (calculando suporte, confiança, lift, etc.) a partir dos itemsets frequentes encontrados pelo `fpgrowth`.
    * (Ela também contém a implementação do `apriori`, que foi considerado mas substituído pelo `fpgrowth`).

## 📊 Exemplos de Visualizações Geradas

* Tabela de Regras de Associação (com métricas e nomes/categorias).
* Gráficos de Barras (Top N regras por Lift/Confiança).
* Gráfico de Dispersão (Suporte vs. Confiança, colorido/dimensionado por Lift).
* Heatmap (Matriz de Confiança ou Lift).
* Grafo de Rede (visualizando conexões entre produtos/categorias).

*(Opcional: Você pode adicionar screenshots das suas visualizações aqui)*

---

*README atualizado em Domingo, 13 de Abril de 2025, 00:15 em São Carlos, Brasil.*
