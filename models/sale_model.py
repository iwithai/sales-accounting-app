# -*- coding: utf-8 -*-

"""
Модель для работы с продажами
"""

from models.base_model import BaseModel
from config import DB_DATE_FORMAT
import sqlite3


class SaleModel(BaseModel):
    """Модель для работы с продажами конкретного магазина"""
    
    def __init__(self, shop_name):
        """Инициализация модели для конкретного магазина"""
        # Заменяем пробелы на подчеркивания для имени таблицы
        table_suffix = shop_name.lower().replace(' ', '_')
        self.shop_name = shop_name
        super().__init__(f"sales_{table_suffix}")
    
    def _create_table(self):
        """Создание таблицы продаж, если её нет"""
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            shop TEXT,
            seller_name TEXT,
            item TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 1,
            price REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL DEFAULT 0
        )
        """
        self._execute_query(query, commit=True)
    
    def add(self, data):
        """Добавление записи с автоматическим расчетом суммы"""
        # Добавляем магазин в данные
        data_with_shop = dict(data)
        if 'shop' not in data_with_shop:
            data_with_shop['shop'] = self.shop_name
        
        # Преобразуем дату
        if 'date' in data_with_shop:
            data_with_shop['date'] = self.format_date_for_db(data_with_shop['date'])
        
        # Рассчитываем сумму
        quantity = float(data_with_shop.get('quantity', 0))
        price = float(data_with_shop.get('price', 0))
        data_with_shop['total'] = quantity * price
        
        return super().add(data_with_shop)
    
    def update(self, id, data):
        """Обновление записи с пересчетом суммы"""
        data_copy = dict(data)
        
        # Преобразуем дату
        if 'date' in data_copy:
            data_copy['date'] = self.format_date_for_db(data_copy['date'])
        
        # Пересчитываем сумму, если изменились количество или цена
        if 'quantity' in data_copy or 'price' in data_copy:
            # Получаем текущие значения
            current = self.get_by_id(id)
            if current:
                quantity = float(data_copy.get('quantity', current['quantity']))
                price = float(data_copy.get('price', current['price']))
                data_copy['total'] = quantity * price
        
        super().update(id, data_copy)
    
    def get_all(self, date_from=None, date_to=None):
        """Получение всех записей с возможностью фильтрации по дате"""
        query = f"SELECT * FROM {self.table_name}"
        params = []
        
        if date_from and date_to:
            query += " WHERE date BETWEEN ? AND ?"
            params = [date_from, date_to]
        elif date_from:
            query += " WHERE date >= ?"
            params = [date_from]
        elif date_to:
            query += " WHERE date <= ?"
            params = [date_to]
        
        query += " ORDER BY date ASC, id ASC"
        
        rows = self._execute_query(query, params, fetchall=True)
        
        # Преобразуем даты в формат отображения
        result = []
        for row in rows:
            row_dict = dict(row)
            row_dict['date'] = self.format_date_for_display(row_dict['date'])
            result.append(row_dict)
        
        return result
    
    def get_total_sum(self, date_from=None, date_to=None):
        """Получение суммы всех продаж за период"""
        query = f"SELECT SUM(total) as total FROM {self.table_name}"
        params = []
        
        if date_from and date_to:
            query += " WHERE date BETWEEN ? AND ?"
            params = [date_from, date_to]
        elif date_from:
            query += " WHERE date >= ?"
            params = [date_from]
        elif date_to:
            query += " WHERE date <= ?"
            params = [date_to]
        
        result = self._execute_query(query, params, fetchone=True)
        return result['total'] if result and result['total'] else 0
