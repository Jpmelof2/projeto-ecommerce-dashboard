# Dicionário de Dados - Data Marts Gold

Os modelos de dados a seguir foram extraídos do banco de dados PostgreSQL do Supabase e representam a camada **Gold** do projeto de e-commerce.

---

## 1. Vendas Temporais (`public_gold_sales.vendas_temporais`)

Esta tabela contém dados agregados de vendas por data, hora e dia da semana.

* **Frequência/Granularidade:** Por data e hora de venda.
* **Colunas:**
  * `data_venda` (`date`): Data da venda.
  * `ano_venda` (`numeric`): Ano correspondente.
  * `mes_venda` (`numeric`): Mês correspondente (1 a 12).
  * `dia_venda` (`numeric`): Dia do mês (1 a 31).
  * `dia_semana_nome` (`text`): Nome do dia da semana (ex: 'Segunda-feira', 'Terça-feira', etc.).
  * `hora_venda` (`numeric`): Hora do dia (0 a 23).
  * `receita_total` (`numeric`): Valor total faturado no período.
  * `quantidade_total` (`numeric`): Quantidade total de itens vendidos.
  * `total_vendas` (`int8`): Quantidade total de pedidos/transações.
  * `total_clientes_unicos` (`int8`): Quantidade de clientes únicos que compraram.
  * `ticket_medio` (`numeric`): Ticket médio do período (`receita_total` / `total_vendas`).

---

## 2. Segmentação de Clientes (`public_gold_cs.clientes_segmentacao`)

Esta tabela contém informações detalhadas por cliente para a área de Customer Success.

* **Frequência/Granularidade:** Um registro por cliente.
* **Colunas:**
  * `cliente_id` (`text`): Identificador único do cliente.
  * `nome_cliente` (`text`): Nome do cliente.
  * `estado` (`text`): Estado da federação do cliente.
  * `receita_total` (`numeric`): Receita total gerada pelo cliente.
  * `total_compras` (`int8`): Total de compras feitas pelo cliente.
  * `ticket_medio` (`numeric`): Ticket médio gasto pelo cliente.
  * `primeira_compra` (`date`): Data da primeira compra do cliente.
  * `ultima_compra` (`date`): Data da última compra registrada do cliente.
  * `segmento_cliente` (`text`): Classificação do cliente (ex: 'VIP', 'TOP_TIER', 'REGULAR').
  * `ranking_receita` (`int8`): Posição do cliente no ranking de maior receita gerada.

---

## 3. Preços e Competitividade (`public_gold_pricing.precos_competitividade`)

Esta tabela armazena o monitoramento de preços do e-commerce frente aos concorrentes.

* **Frequência/Granularidade:** Um registro por produto monitorado.
* **Colunas:**
  * `produto_id` (`text`): Identificador único do produto.
  * `nome_produto` (`text`): Nome do produto.
  * `categoria` (`text`): Categoria do produto.
  * `marca` (`text`): Marca do produto.
  * `nosso_preco` (`numeric`): Nosso preço de venda praticado.
  * `preco_medio_concorrentes` (`numeric`): Preço médio dos concorrentes.
  * `preco_minimo_concorrentes` (`numeric`): Menor preço encontrado na concorrência.
  * `preco_maximo_concorrentes` (`numeric`): Maior preço encontrado na concorrência.
  * `total_concorrentes` (`int8`): Quantidade de concorrentes monitorados para este produto.
  * `diferenca_percentual_vs_media` (`numeric`): Diferença percentual entre nosso preço e a média (`(nosso_preco - preco_medio_concorrentes) / preco_medio_concorrentes * 100`).
  * `diferenca_percentual_vs_minimo` (`numeric`): Diferença percentual entre nosso preço e o mínimo.
  * `classificacao_preco` (`text`): Posicionamento de preço (ex: 'MAIS_CARO_QUE_TODOS', 'MAIS_BARATO_QUE_TODOS', etc.).
  * `receita_total` (`numeric`): Receita total gerada pelo produto.
  * `quantidade_total` (`numeric`): Quantidade total vendida do produto.
