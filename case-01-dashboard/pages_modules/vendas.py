"""
vendas.py — Módulo da página Vendas (Diretor Comercial).

Tabela fonte: public_gold_sales.vendas_temporais

Conteúdo:
  - Filtro: seletor de mês
  - KPIs: Receita Total, Total de Vendas, Ticket Médio, Clientes Únicos
  - Gráfico 1: Receita por Dia (px.line)
  - Gráfico 2: Receita por Dia da Semana (px.bar)
  - Gráfico 3: Vendas por Hora (px.bar)
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.connection import run_query
from utils.formatting import format_currency, format_number

# Paleta de cores consistente
COR_PRIMARIA = "#6C63FF"
COR_SECUNDARIA = "#F7931E"

# Ordem correta dos dias da semana em português
ORDEM_DIAS = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]

# Mapeamento mês → nome
NOMES_MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def _carregar_dados(mes: int | None) -> pd.DataFrame:
    """Busca os dados de vendas_temporais, opcionalmente filtrando por mês."""
    if mes is None:
        sql = "SELECT * FROM public_gold_sales.vendas_temporais ORDER BY data_venda, hora_venda"
    else:
        sql = """
            SELECT *
            FROM public_gold_sales.vendas_temporais
            WHERE mes_venda = %(mes)s
            ORDER BY data_venda, hora_venda
        """
    return run_query(sql, params={"mes": mes} if mes else None)


def _render_kpis(df: pd.DataFrame) -> None:
    """Renderiza os 4 KPIs principais em uma linha de 4 colunas."""
    receita_total = df["receita_total"].sum()
    total_vendas = df["total_vendas"].sum()
    ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
    clientes_unicos = df.groupby("data_venda")["total_clientes_unicos"].max().sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Receita Total",
            value=format_currency(receita_total),
        )
    with col2:
        st.metric(
            label="🛒 Total de Vendas",
            value=format_number(total_vendas),
        )
    with col3:
        st.metric(
            label="🎯 Ticket Médio",
            value=format_currency(ticket_medio),
        )
    with col4:
        st.metric(
            label="👥 Clientes Únicos",
            value=format_number(clientes_unicos),
        )


def _render_grafico_receita_diaria(df: pd.DataFrame) -> None:
    """Gráfico 1 — Receita por Dia (px.line)."""
    receita_dia = (
        df.groupby("data_venda", as_index=False)["receita_total"]
        .sum()
        .sort_values("data_venda")
    )
    receita_dia["data_venda"] = pd.to_datetime(receita_dia["data_venda"])

    fig = px.line(
        receita_dia,
        x="data_venda",
        y="receita_total",
        title="📈 Receita Diária",
        labels={"data_venda": "Data", "receita_total": "Receita (R$)"},
        color_discrete_sequence=[COR_PRIMARIA],
    )
    fig.update_traces(line_width=2.5, mode="lines+markers", marker_size=5)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=18,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        hovermode="x unified",
    )
    fig.update_xaxes(title_text="Data da Venda")
    fig.update_yaxes(title_text="Receita Total (R$)")
    st.plotly_chart(fig, use_container_width=True)


def _render_grafico_dia_semana(df: pd.DataFrame) -> None:
    """Gráfico 2 — Receita por Dia da Semana (px.bar)."""
    receita_semana = (
        df.groupby("dia_semana_nome", as_index=False)["receita_total"].sum()
    )
    # Aplica ordem correta; dias ausentes são colocados no final
    receita_semana["_ordem"] = receita_semana["dia_semana_nome"].apply(
        lambda d: ORDEM_DIAS.index(d) if d in ORDEM_DIAS else 99
    )
    receita_semana = receita_semana.sort_values("_ordem").drop(columns="_ordem")

    fig = px.bar(
        receita_semana,
        x="dia_semana_nome",
        y="receita_total",
        title="📅 Receita por Dia da Semana",
        labels={"dia_semana_nome": "Dia da Semana", "receita_total": "Receita (R$)"},
        color_discrete_sequence=[COR_SECUNDARIA],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=18,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        bargap=0.25,
    )
    fig.update_xaxes(title_text="Dia da Semana")
    fig.update_yaxes(title_text="Receita Total (R$)")
    st.plotly_chart(fig, use_container_width=True)


def _render_grafico_hora(df: pd.DataFrame) -> None:
    """Gráfico 3 — Vendas por Hora (px.bar)."""
    vendas_hora = (
        df.groupby("hora_venda", as_index=False)["total_vendas"]
        .sum()
        .sort_values("hora_venda")
    )
    vendas_hora["hora_venda"] = vendas_hora["hora_venda"].astype(int)

    fig = px.bar(
        vendas_hora,
        x="hora_venda",
        y="total_vendas",
        title="⏰ Volume de Vendas por Hora",
        labels={"hora_venda": "Hora do Dia", "total_vendas": "Total de Vendas"},
        color_discrete_sequence=[COR_PRIMARIA],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=18,
        xaxis=dict(showgrid=False, tickmode="linear", tick0=0, dtick=1),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        bargap=0.2,
    )
    fig.update_xaxes(title_text="Hora do Dia (0–23)")
    fig.update_yaxes(title_text="Total de Vendas")
    st.plotly_chart(fig, use_container_width=True)


def render_vendas() -> None:
    """
    Ponto de entrada da página Vendas.
    Chamada pelo app.py quando o usuário navega para 'Vendas'.
    """
    st.title("🛒 Vendas — Diretor Comercial")
    st.markdown("Análise temporal de receita, volume de vendas e comportamento de compra.")
    st.markdown("---")

    # ------------------------------------------------------------------
    # Filtro de mês
    # ------------------------------------------------------------------
    meses_disponiveis = {0: "Todos os meses"} | {k: v for k, v in NOMES_MESES.items()}
    opcoes = list(meses_disponiveis.values())

    mes_selecionado_nome = st.selectbox(
        "📅 Filtrar por mês:",
        options=opcoes,
        index=0,
    )

    mes_numero = None
    if mes_selecionado_nome != "Todos os meses":
        mes_numero = {v: k for k, v in NOMES_MESES.items()}[mes_selecionado_nome]

    # ------------------------------------------------------------------
    # Carregar dados
    # ------------------------------------------------------------------
    try:
        with st.spinner("Carregando dados de vendas..."):
            df = _carregar_dados(mes_numero)
    except ConnectionError as e:
        st.error(f"🔌 **Erro de conexão:** {e}")
        return
    except RuntimeError as e:
        st.error(f"⚠️ **Erro ao buscar dados:** {e}")
        return

    if df.empty:
        st.warning("Nenhum dado encontrado para o período selecionado.")
        return

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------
    _render_kpis(df)
    st.markdown("---")

    # ------------------------------------------------------------------
    # Gráficos
    # ------------------------------------------------------------------
    _render_grafico_receita_diaria(df)

    col_a, col_b = st.columns(2)
    with col_a:
        _render_grafico_dia_semana(df)
    with col_b:
        _render_grafico_hora(df)
