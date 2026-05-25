"""
app.py — Ponto de entrada do Dashboard Executivo E-commerce.

Case 01 — Imersão de Engenharia de Dados
Stack: Python 3.10+ | Streamlit | Plotly | Pandas | psycopg2

Arquitetura modular:
  utils/connection.py     → conexão com Supabase
  utils/formatting.py     → formatação de valores em R$
  pages_modules/vendas.py   → página Vendas (Diretor Comercial)
  pages_modules/clientes.py → página Clientes (Diretora de Customer Success)
  pages_modules/pricing.py  → página Pricing (Diretor de Pricing)
"""

import streamlit as st

# Configuração global da página — deve ser o primeiro comando Streamlit
st.set_page_config(
    page_title="E-commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Importações dos módulos de página
# ---------------------------------------------------------------------------
from pages_modules.vendas import render_vendas
from pages_modules.clientes import render_clientes
from pages_modules.pricing import render_pricing

# ---------------------------------------------------------------------------
# Sidebar — navegação entre páginas
# ---------------------------------------------------------------------------
st.sidebar.title("E-commerce Analytics")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegar para:",
    options=["Vendas", "Clientes", "Pricing"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.caption("Case 01 — Imersão de Engenharia de Dados")

# ---------------------------------------------------------------------------
# Roteamento de páginas
# ---------------------------------------------------------------------------
if pagina == "Vendas":
    render_vendas()

elif pagina == "Clientes":
    render_clientes()

elif pagina == "Pricing":
    render_pricing()
