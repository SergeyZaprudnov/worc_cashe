from datetime import datetime
from typing import List

def format_date(date_str: str) -> datetime:
    """ Парсинг даты"""
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d')
    except ValueError as e:
        raise ValueError(f"неверный формат даты: {date_str}. Ожидается ДД.ММ.ГГГГ") from e

def calculate_total(operations: List) -> float:
    return sum(op.total_price for op in operations)

def format_currency(amount: float) -> str:
    return f"{amount:,.2f} Р"

def format_date_only(dt) -> str:
    return dt.strftime('%Y-%m-%d')

