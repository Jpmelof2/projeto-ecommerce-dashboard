"""
pricing.py — Módulo da página Pricing (Diretor de Pricing).

Tabela fonte: public_gold_pricing.precos_competitividade

Conteúdo:
  - Filtro: multiselect de categoria
  - KPIs: Total Produtos Monitorados, Mais Caros que Todos,
           Mais Baratos que Todos, Diferença Média vs Mercado
  - Gráfico 1: Distribuição por Classificação (px.pie / donut)
  - Gráfico 2: Diferença % Média por Categoria (px.bar, verde=negativo, vermelho=positivo)
  - Gráfico 3: Scatter — Diferença % vs Volume de Vendas (px.scatter)
  - Tabela de alertas: produtos MAIS_CARO_QUE_TODOS
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.connection import run_query
from utils.formatting import format_currency, format_number, format_percent

# ---------------------------------------------------------------------------
# Paleta de cores — consistente com vendas.py e clientes.py
# ---------------------------------------------------------------------------
COR_PRIMARIA = "#6C63FF"
COR_SECUNDARIA = "#F7931E"
COR_DESTAQUE = "#00D4AA"

# Cores semânticas de pricing
COR_ALERTA = "#FF4B4B"      # mais caro → vermelho
COR_VANTAGEM = "#00D4AA"    # mais barato → verde/teal
COR_NEUTRO = "#F7931E"      # intermediário → laranja

# Mapa de cores por classificação
PALETA_CLASSIFICACAO = {
    "MAIS_CARO_QUE_TODOS": COR_ALERTA,
    "MAIS_BARATO_QUE_TODOS": COR_VANTAGEM,
    "ACIMA_DA_MEDIA": "#FF8C42",
    "ABAIXO_DA_MEDIA": "#36B37E",
    "NA_MEDIA": COR_SECUNDARIA,
}

# Layout comum dos gráficos
_LAYOUT_BASE = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#FAFAFA",
    title_font_size=17,
)


# ---------------------------------------------------------------------------
# Carga de dados
# ---------------------------------------------------------------------------

def _carregar_dados() -> pd.DataFrame:
    """Busca todos os registros de precos_competitividade."""
    sql = """
        SELECT
            produto_id,
            nome_produto,
            categoria,
            marca,
            nosso_preco,
            preco_medio_concorrentes,
            preco_minimo_concorrentes,
            preco_maximo_concorrentes,
            total_concorrentes,
            diferenca_percentual_vs_media,
            diferenca_percentual_vs_minimo,
            classificacao_preco,
            receita_total,
            quantidade_total
        FROM public_gold_pricing.precos_competitividade
        ORDER BY nome_produto
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

def _render_kpis(df: pd.DataFrame) -> None:
    """4 KPIs em st.columns(4)."""
    total_produtos = len(df)
    mais_caros = len(df[df["classificacao_preco"] == "MAIS_CARO_QUE_TODOS"])
    mais_baratos = len(df[df["classificacao_preco"] == "MAIS_BARATO_QUE_TODOS"])
    diff_media = df["diferenca_percentual_vs_media"].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📦 Total Produtos Monitorados",
            value=format_number(total_produtos),
        )
    with col2:
        st.metric(
            label="🔴 Mais Caros que Todos",
            value=format_number(mais_caros),
            help="Produtos cujo nosso preço está acima de TODOS os concorrentes.",
        )
    with col3:
        st.metric(
            label="🟢 Mais Baratos que Todos",
            value=format_number(mais_baratos),
            help="Produtos cujo nosso preço está abaixo de TODOS os concorrentes.",
        )
    with col4:
        sinal = "▲" if diff_media > 0 else "▼" if diff_media < 0 else "—"
        st.metric(
            label="📊 Diferença Média vs Mercado",
            value=format_percent(diff_media),
            help="Média de (nosso preço - preço médio concorrentes) / preço médio. "
                 "Positivo = mais caro; Negativo = mais barato.",
        )


# ---------------------------------------------------------------------------
# Gráfico 1 — Distribuição por Classificação (pizza / donut)
# ---------------------------------------------------------------------------

def _render_grafico_pizza_classificacao(df: pd.DataFrame) -> None:
    """Gráfico 1 — Posicionamento de Preço vs Concorrência (px.pie)."""
    contagem = (
        df["classificacao_preco"]
        .value_counts()
        .reset_index()
    )
    contagem.columns = ["classificacao_preco", "total"]

    fig = px.pie(
        contagem,
        names="classificacao_preco",
        values="total",
        title="🥧 Posicionamento de Preço vs Concorrência",
        color="classificacao_preco",
        color_discrete_map=PALETA_CLASSIFICACAO,
        hole=0.45,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        pull=[0.05] * len(contagem),
    )
    fig.update_layout(
        **_LAYOUT_BASE,
        legend_title_text="Classificação",
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Gráfico 2 — Diferença % Média por Categoria (barras coloridas)
# ---------------------------------------------------------------------------

def _render_grafico_barras_categoria(df: pd.DataFrame) -> None:
    """Gráfico 2 — Competitividade por Categoria (px.bar).

    Barras verdes para valores negativos (mais barato que a média),
    vermelhas para valores positivos (mais caro que a média).
    """
    por_cat = (
        df.groupby("categoria", as_index=False)["diferenca_percentual_vs_media"]
        .mean()
        .sort_values("diferenca_percentual_vs_media")
    )
    por_cat["cor"] = por_cat["diferenca_percentual_vs_media"].apply(
        lambda v: COR_VANTAGEM if v <= 0 else COR_ALERTA
    )

    fig = px.bar(
        por_cat,
        x="categoria",
        y="diferenca_percentual_vs_media",
        title="📊 Competitividade por Categoria",
        color="cor",
        color_discrete_map="identity",
        labels={
            "categoria": "Categoria",
            "diferenca_percentual_vs_media": "Diferença % vs Média",
            "cor": "",
        },
        text=por_cat["diferenca_percentual_vs_media"].apply(
            lambda v: f"{'+' if v > 0 else ''}{v:.1f}%"
        ),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        **_LAYOUT_BASE,
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=True, zerolinecolor="rgba(255,255,255,0.3)"),
        bargap=0.3,
    )
    fig.update_xaxes(title_text="Categoria")
    fig.update_yaxes(title_text="Diferença % Média vs Concorrência")
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Gráfico 3 — Scatter: Diferença % vs Volume de Vendas
# ---------------------------------------------------------------------------

def _render_grafico_scatter(df: pd.DataFrame) -> None:
    """Gráfico 3 — Competitividade x Volume de Vendas (px.scatter)."""
    df_scatter = df.dropna(subset=["diferenca_percentual_vs_media", "quantidade_total", "receita_total"])

    fig = px.scatter(
        df_scatter,
        x="diferenca_percentual_vs_media",
        y="quantidade_total",
        color="classificacao_preco",
        color_discrete_map=PALETA_CLASSIFICACAO,
        size="receita_total",
        size_max=50,
        hover_name="nome_produto",
        hover_data={
            "categoria": True,
            "nosso_preco": ":.2f",
            "diferenca_percentual_vs_media": ":.1f",
            "quantidade_total": True,
            "receita_total": ":.2f",
            "classificacao_preco": False,
        },
        title="🔵 Competitividade x Volume de Vendas",
        labels={
            "diferenca_percentual_vs_media": "Diferença % vs Média Concorrência",
            "quantidade_total": "Quantidade Vendida",
            "classificacao_preco": "Classificação",
        },
    )
    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="rgba(255,255,255,0.4)",
        annotation_text="Na média",
        annotation_position="top right",
        annotation_font_color="rgba(255,255,255,0.6)",
    )
    fig.update_layout(
        **_LAYOUT_BASE,
        legend_title_text="Classificação",
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        height=480,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Tabela de alertas — MAIS_CARO_QUE_TODOS
# ---------------------------------------------------------------------------

def _render_tabela_alertas(df: pd.DataFrame) -> None:
    """Tabela com produtos classificados como MAIS_CARO_QUE_TODOS."""
    st.subheader("🚨 Produtos em Alerta — Mais Caros que Todos os Concorrentes")

    alertas = df[df["classificacao_preco"] == "MAIS_CARO_QUE_TODOS"].copy()

    if alertas.empty:
        st.success("✅ Nenhum produto está mais caro que todos os concorrentes.")
        return

    # Selecionar e renomear colunas conforme PRD
    alertas_exibir = alertas[[
        "produto_id",
        "nome_produto",
        "categoria",
        "nosso_preco",
        "preco_maximo_concorrentes",
        "diferenca_percentual_vs_media",
    ]].copy()

    alertas_exibir["nosso_preco"] = alertas_exibir["nosso_preco"].apply(format_currency)
    alertas_exibir["preco_maximo_concorrentes"] = alertas_exibir["preco_maximo_concorrentes"].apply(format_currency)
    alertas_exibir["diferenca_percentual_vs_media"] = alertas_exibir["diferenca_percentual_vs_media"].apply(
        format_percent
    )

    alertas_exibir = alertas_exibir.rename(columns={
        "produto_id": "ID Produto",
        "nome_produto": "Produto",
        "categoria": "Categoria",
        "nosso_preco": "Nosso Preço",
        "preco_maximo_concorrentes": "Máximo Concorrente",
        "diferenca_percentual_vs_media": "Diferença % vs Média",
    })

    st.dataframe(alertas_exibir, use_container_width=True, hide_index=True)
    st.caption(f"⚠️ {len(alertas)} produto(s) em alerta de sobrepreço.")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def render_pricing() -> None:
    """
    Ponto de entrada da página Pricing.
    Chamada pelo app.py quando o usuário navega para 'Pricing'.
    """
    st.title("💲 Pricing — Competitividade de Preços")
    st.markdown(
        "Monitoramento do posicionamento de preços do e-commerce frente à concorrência."
    )
    st.markdown("---")

    # ------------------------------------------------------------------
    # Carregar dados brutos
    # ------------------------------------------------------------------
    try:
        with st.spinner("Carregando dados de pricing..."):
            df_raw = _carregar_dados()
    except ConnectionError as e:
        st.error(f"🔌 **Erro de conexão:** {e}")
        return
    except RuntimeError as e:
        st.error(f"⚠️ **Erro ao buscar dados:** {e}")
        return

    if df_raw.empty:
        st.warning("Nenhum dado de pricing encontrado.")
        return

    # ------------------------------------------------------------------
    # Filtro: multiselect de categoria
    # ------------------------------------------------------------------
    categorias_disponiveis = sorted(df_raw["categoria"].dropna().unique().tolist())
    categorias_selecionadas = st.multiselect(
        "🏷️ Filtrar por Categoria:",
        options=categorias_disponiveis,
        default=categorias_disponiveis,
        placeholder="Selecione uma ou mais categorias...",
        key="filtro_categoria_pricing",
    )

    # Aplicar filtro; se nada selecionado, mantém tudo
    if categorias_selecionadas:
        df = df_raw[df_raw["categoria"].isin(categorias_selecionadas)].copy()
    else:
        df = df_raw.copy()

    if df.empty:
        st.warning("Nenhum produto encontrado para as categorias selecionadas.")
        return

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------
    _render_kpis(df)
    st.markdown("---")

    # ------------------------------------------------------------------
    # Gráficos — linha 1: pizza + barras por categoria (lado a lado)
    # ------------------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        _render_grafico_pizza_classificacao(df)
    with col2:
        _render_grafico_barras_categoria(df)

    # ------------------------------------------------------------------
    # Gráfico 3 — Scatter (largura total)
    # ------------------------------------------------------------------
    _render_grafico_scatter(df)

    st.markdown("---")

    # ------------------------------------------------------------------
    # Tabela de alertas
    # ------------------------------------------------------------------
    _render_tabela_alertas(df)
