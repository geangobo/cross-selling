# -*- coding: utf-8 -*-
"""
Script para Análise de Cesta de Compras (Market Basket Analysis)
Utilizando o dataset Olist, Polars para pré-processamento inicial,
Pandas para agrupamento em lista (workaround), e FP-Growth (mlxtend).

Objetivo: Encontrar regras de associação entre produtos ou categorias,
          com foco em regras intercategorias.
"""

import polars as pl
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import warnings
import time

# --- Configurações e Parâmetros ---

# Caminhos para os arquivos de dados (ajuste se necessário)
PATH_ORDERS = "../data/olist_orders_dataset.csv"
PATH_ORDER_ITEMS = "../data/olist_order_items_dataset.csv"
PATH_PRODUCTS = "../data/olist_products_dataset.csv"
OUTPUT_FILENAME = 'regras_fpgrowth_olist_final.xlsx' # Nome do arquivo de saída Excel

# Parâmetros de Filtragem e Algoritmo (AJUSTE CONFORME NECESSÁRIO)
STATUS_VALIDOS = ['delivered'] # Status dos pedidos a serem considerados
MIN_ITEM_FREQUENCY = 50       # Nº mínimo de cestas em que um produto deve aparecer para ser incluído
MIN_SUPPORT_FPGROWTH = 0.00005 # Suporte mínimo para FP-Growth (comece baixo)
RULE_METRIC = "lift"          # Métrica para filtrar regras ('lift' ou 'confidence')
MIN_THRESHOLD_RULES = 1       # Limiar mínimo para a métrica ('lift' >= 1 ou 'confidence' >= 0.x)
FILTER_CROSS_CATEGORY = True  # Define se filtra para mostrar apenas regras intercategorias no final
SAVE_CROSS_CATEGORY_ONLY = True # Se True e FILTER_CROSS_CATEGORY=True, salva apenas intercategorias

# --- Ignorar Warnings --
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# --- Funções Auxiliares ---

def reportar_nulos_polars(df: pl.DataFrame, nome_df: str):
    """Verifica e reporta nulos em DataFrame Polars."""
    print(f"\n--- Verificando Nulos em '{nome_df}' ---")
    df_null_counts = df.null_count()
    df_null_long = df_null_counts.unpivot()
    df_null_filtered = df_null_long.filter(pl.col("value") > 0)
    print("Colunas com valores nulos e suas contagens:")
    if df_null_filtered.height == 0:
        print("Nenhuma coluna com valores nulos encontrada.")
    else:
        for row_dict in df_null_filtered.iter_rows(named=True):
            print(f"- {row_dict['variable']}: {row_dict['value']}")
    total_nulos = df_null_long['value'].sum()
    print(f"\nTotal de valores nulos no DataFrame '{nome_df}': {total_nulos}")
    print("-" * (len(f"--- Verificando Nulos em '{nome_df}' ---") + 4))

def get_info_from_itemset(itemset, mapa):
    """Busca informação (nome/categoria) para um frozenset de IDs."""
    # Os IDs no itemset já devem ser strings (product_id)
    items = [mapa.get(item, f"Info({item})?") for item in itemset]
    # Retorna ordenado e separado por vírgula
    return ', '.join(sorted(items))

# --- Início do Script ---
start_time = time.time()
print("==============================================")
print("=== INICIANDO ANÁLISE DE CESTA DE COMPRAS ===")
print("==============================================")
print(f"Versão do Polars: {pl.__version__}")
print(f"Versão do Pandas: {pd.__version__}")

# --- 1. Carregar os Dados ---
print("\n--- 1. Carregando Datasets Olist ---")
try:
    orders = pl.read_csv(PATH_ORDERS)
    order_items = pl.read_csv(PATH_ORDER_ITEMS)
    products = pl.read_csv(PATH_PRODUCTS)
    print(f"Orders carregado: {orders.shape}")
    print(f"Order Items carregado: {order_items.shape}")
    print(f"Products carregado: {products.shape}")
except Exception as e:
    print(f"Erro fatal ao carregar arquivos CSV: {e}")
    exit()

# --- 2. Verificar Nulos (Opcional) ---
# reportar_nulos_polars(orders, "orders")
# reportar_nulos_polars(order_items, "order_items")
# reportar_nulos_polars(products, "products")

# --- 3. Preparação Inicial dos Dados (Polars) ---
print("\n--- 3. Preparação Inicial (Polars) ---")
try:
    # 3.1 Juntar Pedidos com Itens
    print("Passo 3.1: Juntando orders e order_items...")
    order_details = order_items.join(orders, on='order_id', how='inner')

    # 3.2 Filtrar Pedidos Válidos
    order_details_filtered = order_details.filter(pl.col('order_status').is_in(STATUS_VALIDOS))
    print(f"Passo 3.2: Mantidos {order_details_filtered.shape[0]} itens de pedidos com status: {STATUS_VALIDOS}")

    # 3.3 Selecionar Colunas Chave e Garantir Tipos
    print("Passo 3.3 & 3.4: Selecionando e tipando colunas (order_id, product_id)...")
    baskets_raw = order_details_filtered.select(['order_id', 'product_id'])
    baskets_typed = baskets_raw.with_columns(
        pl.col('product_id').cast(pl.Utf8),
        pl.col('order_id').cast(pl.Utf8)
    )

    # 3.4 Remover Duplicatas (mesmo produto no mesmo pedido)
    print("Passo 3.5: Removendo produtos duplicados dentro do mesmo pedido...")
    basket_items_unique = baskets_typed.unique(subset=['order_id', 'product_id'], keep='first')
    print(f"Itens únicos em cestas válidas: {basket_items_unique.shape[0]}")

    # 3.5 Filtrar Produtos Pouco Frequentes
    print(f"Passo 3.6: Filtrando produtos com frequência < {MIN_ITEM_FREQUENCY}...")
    item_counts = basket_items_unique.group_by('product_id').agg(pl.count().alias('counts'))
    frequent_items_ids = item_counts.filter(pl.col('counts') >= MIN_ITEM_FREQUENCY)['product_id']
    basket_items_filtered = basket_items_unique.filter(pl.col('product_id').is_in(frequent_items_ids))
    num_produtos_originais = basket_items_unique['product_id'].n_unique()
    num_produtos_restantes = frequent_items_ids.shape[0]
    print(f"Produtos únicos originais: {num_produtos_originais}")
    print(f"Produtos únicos restantes para análise: {num_produtos_restantes}")
    print(f"Itens restantes nas cestas após filtro: {basket_items_filtered.shape[0]}")

except Exception as e:
    print(f"Erro durante a preparação inicial com Polars: {e}")
    exit()

# --- 4. Agrupamento em Lista (Workaround com Pandas) ---
print("\n--- 4. Agrupamento em Lista (Pandas Workaround) ---")
transactions_list = None
if basket_items_filtered.height > 0:
    try:
        basket_items_unique_pd = basket_items_filtered.to_pandas()
        print(f"Convertido para Pandas. Shape: {basket_items_unique_pd.shape}")
        transactions_list = basket_items_unique_pd.groupby('order_id')['product_id'].apply(list).tolist()
        print(f"Agrupamento com Pandas concluído. Número de cestas: {len(transactions_list)}")
    except Exception as e:
        print(f"Erro durante Conversão/Agrupamento Pandas: {e}")
else:
    print("Nenhum item restou após a filtragem de produtos infrequentes. Análise interrompida.")
    exit()

# --- 5. Codificação e Análise de Regras (mlxtend) ---
if transactions_list:
    print("\n--- 5. Codificação e Análise de Regras (mlxtend) ---")
    # 5.1 TransactionEncoder
    print("Passo 5.1: Aplicando TransactionEncoder...")
    try:
        te = TransactionEncoder()
        te_ary = te.fit(transactions_list).transform(transactions_list)
        df_encoded_pd = pd.DataFrame(te_ary, columns=te.columns_)
        print(f"DataFrame one-hot encoded (Pandas) criado. Shape: {df_encoded_pd.shape}")
    except MemoryError:
         print("\nERRO DE MEMÓRIA: Não foi possível criar a matriz one-hot encoded.")
         print("Tente aumentar o valor de 'MIN_ITEM_FREQUENCY' no início do script.")
         exit()
    except Exception as e:
         print(f"Erro no TransactionEncoder ou criação do DataFrame: {e}")
         exit()

    # 5.2 FP-Growth
    print(f"\nPasso 5.2: Executando fpgrowth com min_support = {MIN_SUPPORT_FPGROWTH}...")
    try:
        frequent_itemsets = fpgrowth(df_encoded_pd, min_support=MIN_SUPPORT_FPGROWTH, use_colnames=True)
        print("FP-Growth concluído.")
    except MemoryError:
         print("\nERRO DE MEMÓRIA: Não foi possível executar o FP-Growth.")
         print("Tente aumentar o valor de 'MIN_ITEM_FREQUENCY' ou 'MIN_SUPPORT_FPGROWTH'.")
         exit()
    except Exception as e:
        print(f"Erro durante o FP-Growth: {e}")
        frequent_itemsets = pd.DataFrame() # Cria dataframe vazio para evitar erro abaixo

    # 5.3 Geração de Regras
    if not frequent_itemsets.empty:
        frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
        print(f"Encontrados {frequent_itemsets.shape[0]} itemsets frequentes.")
        num_multi_itemsets = len(frequent_itemsets[frequent_itemsets['length'] >= 2])
        print(f"Número de itemsets com mais de 1 item: {num_multi_itemsets}")

        if num_multi_itemsets > 0:
            print(f"\nPasso 5.3: Gerando regras com {RULE_METRIC} >= {MIN_THRESHOLD_RULES}...")
            rules = association_rules(frequent_itemsets, metric=RULE_METRIC, min_threshold=MIN_THRESHOLD_RULES)
            print(f"Regras geradas. Encontradas {rules.shape[0]} regras.")

            # --- 6. Enriquecimento e Filtragem Final ---
            if not rules.empty:
                print("\n--- 6. Enriquecimento e Pós-Processamento ---")
                # 6.1 Adicionar Nomes de Categoria
                print("Passo 6.1: Adicionando nomes de categoria...")
                try:
                    mapa_categorias = products.select(['product_id', 'product_category_name'])\
                                              .fill_null("Desconhecida")\
                                              .with_columns(pl.col('product_id').cast(pl.Utf8))\
                                              .unique(subset=['product_id'], keep='first')\
                                              .to_pandas()\
                                              .set_index('product_id')['product_category_name']\
                                              .to_dict()

                    # Usa a função auxiliar definida no início
                    rules['Categoria_Antecedent'] = rules['antecedents'].apply(lambda x: get_info_from_itemset(x, mapa_categorias))
                    rules['Categoria_Consequent'] = rules['consequents'].apply(lambda x: get_info_from_itemset(x, mapa_categorias))
                    # Usando categoria como nome por falta de nome de produto fácil no dataset Olist
                    rules['Nomes_Antecedents'] = rules['Categoria_Antecedent']
                    rules['Nomes_Consequents'] = rules['Categoria_Consequent']
                    print("Nomes/Categorias adicionados.")
                except Exception as e:
                    print(f"Erro ao adicionar nomes/categorias: {e}. Continuando sem eles.")

                # 6.2 Filtrar Regras Intercategorias (se solicitado)
                if FILTER_CROSS_CATEGORY:
                    print("\nPasso 6.2: Filtrando regras intercategorias...")
                    if 'Categoria_Antecedent' in rules.columns and 'Categoria_Consequent' in rules.columns:
                        regras_para_salvar = rules[rules['Categoria_Antecedent'] != rules['Categoria_Consequent']].copy()
                        print(f"Mantidas {len(regras_para_salvar)} regras intercategorias.")
                        if regras_para_salvar.empty and not rules.empty:
                             print("Aviso: Nenhuma regra INTERCATEGORIA encontrada com os filtros atuais. Todas as regras encontradas eram INTRACATEGORIA.")
                             print("Salvando as regras INTRACATEGORIA para referência.")
                             regras_para_salvar = rules.copy() # Salva as regras originais se nenhuma intercategoria foi encontrada
                    else:
                        print("Colunas de categoria não encontradas. Não foi possível filtrar regras intercategorias.")
                        regras_para_salvar = rules.copy()
                else:
                    regras_para_salvar = rules.copy()

                # 6.3 Ordenar e Salvar Resultados
                if not regras_para_salvar.empty:
                     output_to_save = regras_para_salvar.sort_values(RULE_METRIC, ascending=False)
                     print(f"\nPasso 6.3: Salvando {len(output_to_save)} regras em {OUTPUT_FILENAME}...")
                     try:
                         output_to_save.to_excel(OUTPUT_FILENAME, index=False, engine='openpyxl')
                         print("Resultados salvos com sucesso.")
                     except Exception as e:
                         print(f"Erro ao salvar o arquivo Excel: {e}")
                else:
                     print("\nNenhuma regra final para salvar após filtros.")

            else: # Se rules estava vazia
                 print("\nNenhuma regra encontrada com os critérios de métrica/limiar definidos.")
        else: # Se não haviam multi-itemsets
            print("\nNão foram encontrados itemsets com 2 ou mais itens.")
            print("Considere diminuir 'MIN_SUPPORT_FPGROWTH' ou 'MIN_ITEM_FREQUENCY'.")
    else: # Se frequent_itemsets estava vazio
        print("\nNenhum itemset frequente encontrado pelo FP-Growth.")
        print("Verifique 'MIN_SUPPORT_FPGROWTH' ou os dados de entrada.")
else: # Se transactions_list falhou
    print("\nErro na preparação da lista de transações. Análise interrompida.")

# --- Fim do Script ---
end_time = time.time()
print("\n==============================================")
print(f"=== ANÁLISE CONCLUÍDA (Tempo: {end_time - start_time:.2f} segundos) ===")
print("==============================================")