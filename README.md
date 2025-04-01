# 🛒 Análise de Cesta de Compras com Polars e Mlxtend

## 🎯 Objetivo do Projeto

Este projeto realiza uma Análise de Cesta de Compras utilizando dados transacionais (itens de notas fiscais), com manipulação de dados performática via Polars. O objetivo principal é identificar regras de associação do tipo "SE compra Produto X, ENTÃO compra Produto Y", descobrindo quais produtos são frequentemente comprados juntos e a força dessas associações. Os insights podem ser usados para estratégias de cross-selling, otimização de layout, promoções e sistemas de recomendação.

## 🛠️ Tecnologias Utilizadas

* **Python 3.9.13**
* **Polars:** Para manipulação e preparação de dados de alta performance.
* **Mlxtend:** Para implementação do algoritmo Apriori e geração das regras de associação.
* Matplotlib & Seaborn: Para visualização de dados (gráficos de barras, dispersão, heatmaps).
* NetworkX: Para criação e visualização do grafo de associação de produtos (se utilizado).

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
    Certifique-se de ter um arquivo `requirements.txt` no seu projeto que inclua `polars`, `mlxtend`, `matplotlib`, `seaborn`, `networkx`, `openpyxl` (ou `xlsxwriter`), etc. Se não tiver, você pode gerá-lo (após instalar as bibliotecas no seu ambiente) com `pip freeze > requirements.txt`.
    Para instalar os pacotes necessários, execute:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Execução da Análise

1.  **Dados de Entrada:** Coloque o arquivo de dados brutos (ex: `.xlsx` ou `.csv`) na pasta `/data/` (ou conforme configurado no notebook e no `.gitignore`).
2.  **Execute o Notebook:** Abra e execute as células do Jupyter Notebook principal localizado em `src/`. O notebook utiliza **Polars** para leitura e manipulação eficiente dos dados antes de aplicar a análise de cesta com `mlxtend`.
3.  **Resultados:** O notebook irá gerar:
    * Visualizações diretamente nas células.
    * Um arquivo Excel (ex: `regras_associacao_com_nomes.xlsx`) ou outro formato contendo a tabela final com as regras de associação, métricas e nomes dos produtos.

## 💡 Conceitos Chave

* **Análise de Cesta (Market Basket Analysis):** 🧺 É uma técnica de mineração de dados usada principalmente no varejo para descobrir relacionamentos ou padrões de coocorrência entre itens que são comprados juntos pelos clientes. O exemplo clássico é a descoberta da associação entre fraldas e cervejas. Ajuda a entender o comportamento de compra.

* **Algoritmo Apriori:** 📊 É um algoritmo clássico e fundamental para a Análise de Cesta. Ele funciona em duas etapas principais:
    1.  **Encontrar Itemsets Frequentes:** Identifica todos os conjuntos de itens que aparecem juntos em um número de transações acima de um limiar mínimo especificado (o *suporte mínimo*). Ele faz isso de forma eficiente usando a propriedade "Apriori": se um conjunto de itens é frequente, todos os seus subconjuntos também devem ser frequentes.
    2.  **Gerar Regras de Associação:** A partir dos itemsets frequentes encontrados, ele gera regras (como X -> Y) que atendem a um limiar mínimo de outra métrica, geralmente a *confiança mínima* ou *lift mínimo*.

* **Biblioteca `mlxtend`:** 🐍 É uma biblioteca Python que oferece implementações eficientes e fáceis de usar para várias tarefas de machine learning e mineração de dados, incluindo:
    * `mlxtend.frequent_patterns.apriori`: Função para encontrar itemsets frequentes.
    * `mlxtend.frequent_patterns.association_rules`: Função para gerar as regras de associação (calculando suporte, confiança, lift, etc.) a partir dos itemsets frequentes.
    * **Importante:** A entrada para `mlxtend.frequent_patterns.apriori` precisa ser um DataFrame (geralmente Pandas, mas pode aceitar outros formatos como arrays NumPy ou DataFrames Polars convertidos) no formato one-hot encoded (transações x itens). Pode ser necessário converter o resultado do agrupamento feito com Polars para o formato esperado pelo `apriori`.

## 📊 Exemplos de Visualizações Geradas

* Tabela de Regras de Associação (com métricas e nomes).
* Gráficos de Barras (Top N regras por Lift/Confiança).
* Gráfico de Dispersão (Suporte vs. Confiança, colorido/dimensionado por Lift).
* Heatmap (Matriz de Confiança ou Lift).
* Grafo de Rede (visualizando conexões entre produtos).
