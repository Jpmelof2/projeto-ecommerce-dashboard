"""
formatting.py — Módulo de funções utilitárias de formatação.

Responsabilidade: centralizar todas as formatações de valores monetários
e numéricos no padrão brasileiro (R$, ponto de milhar, vírgula decimal).

Uso:
    from utils.formatting import format_currency, format_number, format_percent
"""


def format_currency(value: float) -> str:
    """
    Formata um valor numérico como moeda brasileira.

    Exemplos:
        1234567.89  →  "R$ 1.234.567,89"
        1500.5      →  "R$ 1.500,50"
        0           →  "R$ 0,00"

    Args:
        value (float): Valor numérico a ser formatado.

    Returns:
        str: String formatada no padrão R$ X.XXX,XX
    """
    if value is None:
        return "R$ -"
    try:
        # Formata com 2 casas decimais usando locale pt-BR manualmente
        formatted = f"{float(value):,.2f}"          # "1,234,567.89" (padrão US)
        formatted = formatted.replace(",", "X")     # separador temporário
        formatted = formatted.replace(".", ",")     # . → ,  (decimal)
        formatted = formatted.replace("X", ".")     # X → .  (milhar)
        return f"R$ {formatted}"
    except (TypeError, ValueError):
        return "R$ -"


def format_number(value: float, decimals: int = 0) -> str:
    """
    Formata um número inteiro ou decimal com separador de milhar brasileiro.

    Exemplos:
        1234567   →  "1.234.567"
        1500.5    →  "1.500,5"

    Args:
        value (float): Valor numérico a ser formatado.
        decimals (int): Número de casas decimais. Padrão: 0.

    Returns:
        str: String formatada com ponto de milhar e vírgula decimal.
    """
    if value is None:
        return "-"
    try:
        formatted = f"{float(value):,.{decimals}f}"
        formatted = formatted.replace(",", "X")
        formatted = formatted.replace(".", ",")
        formatted = formatted.replace("X", ".")
        return formatted
    except (TypeError, ValueError):
        return "-"


def format_percent(value: float, decimals: int = 1) -> str:
    """
    Formata um valor percentual com sinal de + ou - e símbolo %.

    Exemplos:
        5.3   →  "+5,3%"
        -2.1  →  "-2,1%"
        0.0   →  "0,0%"

    Args:
        value (float): Percentual a ser formatado.
        decimals (int): Número de casas decimais. Padrão: 1.

    Returns:
        str: String formatada com sinal e símbolo %.
    """
    if value is None:
        return "-"
    try:
        val = float(value)
        sign = "+" if val > 0 else ""
        formatted = f"{val:.{decimals}f}".replace(".", ",")
        return f"{sign}{formatted}%"
    except (TypeError, ValueError):
        return "-"
