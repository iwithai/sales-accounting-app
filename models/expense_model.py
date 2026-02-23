# -*- coding: utf-8 -*-

"""
Модель для работы с расходами
"""

from models.base_model import BaseModel


class ExpenseModel(BaseModel):
    """Модель для работы с расходами"""
    
    def __init__(self):
        super().__init__("expenses")
    
    def _create_table(self):
        """Создание таблицы расходов"""
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            shop TEXT NOT NULL,
            item TEXT NOT NULL,
            descr TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0
        )
        """
        self._execute_query(query, commit=True)
    
    def add(self, data):
        """Добавление записи о расходе"""
        data_copy = dict(data)
        
        # Преобразуем дату
        if 'date' in data_copy:
            data_copy['date'] = self.format_date_for_db(data_copy['date'])
        
        return super().add(data_copy)
    
    def update(self, id, data):
        """Обновление записи"""
        data_copy = dict(data)
        
        # Преобразуем дату
        if 'date' in data_copy:
            data_copy['date'] = self.format_date_for_db(data_copy['date'])
        
        super().update(id, data_copy)
    
    def get_all(self, date_from=None, date_to=None, shop=None):
        """Получение всех записей с фильтрацией"""
        query = "SELECT * FROM expenses"
        conditions = []
        params = []
        
        if date_from and date_to:
            conditions.append("date BETWEEN ? AND ?")
            params.extend([date_from, date_to])
        
        if shop and shop != "Все":
            conditions.append("shop = ?")
            params.append(shop)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC, id ASC"
        
        rows = self._execute_query(query, params, fetchall=True)
        
        # Преобразуем даты
        result = []
        for row in rows:
            row_dict = dict(row)
            row_dict['date'] = self.format_date_for_display(row_dict['date'])
            result.append(row_dict)
        
        return result
    
    def get_total_sum(self, date_from=None, date_to=None, shop=None):
        """Получение суммы расходов за период"""
        query = "SELECT SUM(amount) as total FROM expenses"
        conditions = []
        params = []
        
        if date_from and date_to:
            conditions.append("date BETWEEN ? AND ?")
            params.extend([date_from, date_to])
        
        if shop and shop != "Все":
            conditions.append("shop = ?")
            params.append(shop)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        result = self._execute_query(query, params, fetchone=True)
        return result['total'] if result and result['total'] else 0
