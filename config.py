# -*- coding: utf-8 -*-

"""
Конфигурационный файл приложения
"""

import os
from pathlib import Path

# База данных
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "finance.db"

# Настройки таблиц
DATE_FORMAT = "%d.%m.%Y"
DB_DATE_FORMAT = "%Y-%m-%d"

# Магазины
SHOPS = ["М1", "М2"]

# Цвета
COLORS = {
    'bg': '#f0f0f0',
    'fg': '#000000',
    'select': "#c4dcef",
    'profit_positive': '#008000',
    'profit_negative': '#ff0000',
    'header_bg': '#e1e1e1',
    'table_bg': '#ffffff',
    'table_alternate': '#f5f5f5'
}

# Настройки таблицы
TABLE_FONT = ('Arial', 10)
HEADER_FONT = ('Arial', 10, 'bold')

# Поля для таблиц
SALES_COLUMNS = {
    'seller_name': {'text': 'Продавец', 'width': 120, 'editable': True},
    'item': {'text': 'Товар', 'width': 200, 'editable': True},
    'quantity': {'text': 'Кол-во', 'width': 80, 'editable': True},
    'price': {'text': 'Цена', 'width': 100, 'editable': True},
    'total': {'text': 'Сумма', 'width': 100, 'editable': False}
}

EXPENSE_COLUMNS = {
    'shop': {'text': 'Магазин', 'width': 100, 'editable': True},
    'item': {'text': 'Наименование', 'width': 300, 'editable': True},
    'amount': {'text': 'Сумма', 'width': 120, 'editable': True}
}
