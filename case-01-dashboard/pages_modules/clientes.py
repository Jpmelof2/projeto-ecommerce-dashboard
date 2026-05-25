"""
clientes.py — Módulo da página Clientes (Diretora de Customer Success).

Tabela fonte: public_gold_cs.clientes_segmentacao

Conteúdo:
  - KPIs: Total Clientes, Clientes VIP, Receita VIP, Ticket Médio Geral
  - Gráfico 1: Distribuição por Segmento (px.pie)
  - Gráfico 2: Receita por Segmento (px.bar)
  - Gráfico 3: Top 10 Clientes por Receita (px.bar horizontal)
  - Gráfico 4: Clientes por Estado (px.bar)
  - Tabela detalhada com filtro por segmento
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.connection import run_query
from utils.formatting import format_currency, format_number

# Paleta consistente com vendas.py
COR_PRIMARIA = "#6C63FF"
COR_SECUNDARIA = "#F7931E"
COR_DESTAQUE = "#00D4AA"

PALETA_SEGMENTOS = {
    "VIP": "#F7931E",
    "TOP_TIER": "#6C63FF",
    "REGULAR": "#00D4AA",
}


# ---------------------------------------------------------------------------
# Carga de dados
# ---------------------------------------------------------------------------

def _carregar_dados() -> pd.DataFrame:
    """Busca todos os registros de clientes_segmentacao."""
    sql = """
        SELECT
            cliente_id,
            nome_cliente,
            estado,
            receita_total,
            total_compras,
            ticket_medio,
            primeira_compra,
            ultima_compra,
            segmento_cliente,
            ranking_receita
        FROM public_gold_cs.clientes_segmentacao
        ORDER BY ranking_receita
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

def _render_kpis(df: pd.DataFrame) -> None:
    """4 KPIs em st.columns(4)."""
    total_clientes = len(df)
    clientes_vip = len(df[df["segmento_cliente"] == "VIP"])
    receita_vip = df.loc[df["segmento_cliente"] == "VIP", "receita_total"].sum()
    ticket_medio_geral = df["ticket_medio"].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="👤 Total Clientes", value=format_number(total_clientes))
    with col2:
        st.metric(label="⭐ Clientes VIP", value=format_number(clientes_vip))
    with col3:
        st.metric(label="💎 Receita VIP", value=format_currency(receita_vip))
    with col4:
        st.metric(label="🎯 Ticket Médio Geral", value=format_currency(ticket_medio_geral))


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def _render_grafico_pizza_segmento(df: pd.DataFrame) -> None:
    """Gráfico 1 — Distribuição de Clientes por Segmento (px.pie)."""
    contagem = df["segmento_cliente"].value_counts().reset_index()
    contagem.columns = ["segmento_cliente", "total"]

    fig = px.pie(
        contagem,
        names="segmento_cliente",
        values="total",
        title="🥧 Distribuição de Clientes por Segmento",
        color="segmento_cliente",
        color_discrete_map=PALETA_SEGMENTOS,
        hole=0.45,  # donut
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        pull=[0.05] * len(contagem),
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=17,
        legend_title_text="Segmento",
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_grafico_receita_segmento(df: pd.DataFrame) -> None:
    """Gráfico 2 — Receita por Segmento (px.bar)."""
    receita_seg = (
        df.groupby("segmento_cliente", as_index=False)["receita_total"].sum()
        .sort_values("receita_total", ascending=False)
    )

    fig = px.bar(
        receita_seg,
        x="segmento_cliente",
        y="receita_total",
        title="📊 Receita por Segmento",
        color="segmento_cliente",
        color_discrete_map=PALETA_SEGMENTOS,
        labels={"segmento_cliente": "Segmento", "receita_total": "Receita (R$)"},
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=17,
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        bargap=0.3,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_grafico_top10(df: pd.DataFrame) -> None:
    """Gráfico 3 — Top 10 Clientes por Receita (px.bar horizontal)."""
    top10 = (
        df.nsmallest(10, "ranking_receita")
        .sort_values("receita_total", ascending=True)  # menor embaixo → maior no topo
    )

    fig = px.bar(
        top10,
        x="receita_total",
        y="nome_cliente",
        orientation="h",
        title="🏆 Top 10 Clientes por Receita",
        color="segmento_cliente",
        color_discrete_map=PALETA_SEGMENTOS,
        labels={"receita_total": "Receita Total (R$)", "nome_cliente": "Cliente"},
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=17,
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=False),
        legend_title_text="Segmento",
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_grafico_clientes_estado(df: pd.DataFrame) -> None:
    """Gráfico 4 — Clientes por Estado (px.bar), ordenado por quantidade DESC."""
    por_estado = (
        df.groupby("estado", as_index=False)
        .size()
        .rename(columns={"size": "total_clientes"})
        .sort_values("total_clientes", ascending=False)
    )

    fig = px.bar(
        por_estado,
        x="estado",
        y="total_clientes",
        title="🗺️ Clientes por Estado",
        color_discrete_sequence=[COR_PRIMARIA],
        labels={"estado": "Estado", "total_clientes": "Nº de Clientes"},
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=17,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        bargap=0.2,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Tabela detalhada
# ---------------------------------------------------------------------------

def _render_tabela(df: pd.DataFrame) -> None:
    """Tabela detalhada com filtro por segmento."""
    st.subheader("📋 Tabela Detalhada de Clientes")

    segmentos_disponiveis = ["Todos"] + sorted(df["segmento_cliente"].unique().tolist())
    segmento_filtro = st.selectbox(
        "Filtrar por segmento:",
        options=segmentos_disponiveis,
        index=0,
        key="filtro_segmento_tabela",
    )

    df_filtrado = (
        df if segmento_filtro == "Todos"
        else df[df["segmento_cliente"] == segmento_filtro]
    )

    # Colunas formatadas para exibição
    df_exibir = df_filtrado.copy()
    df_exibir["receita_total"] = df_exibir["receita_total"].apply(format_currency)
    df_exibir["ticket_medio"] = df_exibir["ticket_medio"].apply(format_currency)
    df_exibir = df_exibir.rename(columns={
        "cliente_id": "ID",
        "nome_cliente": "Nome",
        "estado": "Estado",
        "receita_total": "Receita Total",
        "total_compras": "Compras",
        "ticket_medio": "Ticket Médio",
        "primeira_compra": "1ª Compra",
        "ultima_compra": "Última Compra",
        "segmento_cliente": "Segmento",
        "ranking_receita": "Ranking",
    })

    st.dataframe(
        df_exibir,
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"{len(df_filtrado)} clientes exibidos.")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def render_clientes() -> None:
    """
    Ponto de entrada da página Clientes.
    Chamada pelo app.py quando o usuário navega para 'Clientes'.
    """
    st.title("👥 Clientes — Customer Success")
    st.markdown("Segmentação e análise de comportamento dos clientes do e-commerce.")
    st.markdown("---")

    # ------------------------------------------------------------------
    # Carregar dados
    # ------------------------------------------------------------------
    try:
        with st.spinner("Carregando dados de clientes..."):
            df = _carregar_dados()
    except ConnectionError as e:
        st.error(f"🔌 **Erro de conexão:** {e}")
        return
    except RuntimeError as e:
        st.error(f"⚠️ **Erro ao buscar dados:** {e}")
        return

    if df.empty:
        st.warning("Nenhum dado de clientes encontrado.")
        return

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------
    _render_kpis(df)
    st.markdown("---")

    # ------------------------------------------------------------------
    # Gráficos — linha 1: pizza + barras receita por segmento
    # ------------------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        _render_grafico_pizza_segmento(df)
    with col2:
        _render_grafico_receita_segmento(df)

    # ------------------------------------------------------------------
    # Gráfico 3 — Top 10 (largura total)
    # ------------------------------------------------------------------
    _render_grafico_top10(df)

    # ------------------------------------------------------------------
    # Gráfico 4 — Clientes por Estado (largura total)
    # ------------------------------------------------------------------
    _render_grafico_clientes_estado(df)

    st.markdown("---")

    # ------------------------------------------------------------------
    # Tabela detalhada
    # ------------------------------------------------------------------
    _render_tabela(df)
