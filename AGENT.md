# Case 01 — Dashboard Executivo E-commerce

## Contexto

Projeto da Imersão de Engenharia de Dados.

Objetivo:
Construir um dashboard executivo em Streamlit para três diretorias de um e-commerce.

Diretorias:

1. Comercial
2. Customer Success
3. Pricing

Consumindo os Data Marts Gold do Supabase.

---

## Data Marts disponíveis

### Vendas
public_gold_sales.vendas_temporais

Objetivo:
- Receita diária
- Ticket médio
- Volume de vendas
- Melhor dia da semana
- Performance temporal

### Clientes
public_gold_cs.clientes_segmentacao

Objetivo:
- Clientes VIP
- Segmentação
- Distribuição geográfica
- Clientes em risco

### Pricing
public_gold_pricing.precos_competitividade

Objetivo:
- Produtos mais caros que concorrentes
- Categorias fora do mercado
- Alertas competitivos

---

## Stack

- Python 3.13
- Streamlit
- Plotly
- Pandas
- psycopg2-binary
- python-dotenv
- Supabase PostgreSQL

---

## Banco de Dados

Conectar ao Supabase PostgreSQL.

Usar variáveis de ambiente no `.env`.

Contexto disponível em:

- `.llm/database.md`
- `.llm/prd.md`

Usar MCP do Supabase quando necessário.

---

## Regras

- NÃO adicionar funcionalidades extras além do PRD
- Arquitetura modular
- Código limpo e organizado
- Plotly para gráficos
- NÃO usar matplotlib
- Valores monetários em reais (R$)
- Layout profissional
- Dashboard em wide mode
- Validar cada etapa antes de avançar
- Não commitar `.env`

---

## Metodologia

1. Explorar contexto
2. Planejar antes de desenvolver
3. Desenvolver em pequenas etapas
4. Validar antes de continuar

Sempre ler:

- AGENT.md
- .llm/prd.md
- .llm/database.md

antes de implementar qualquer código.