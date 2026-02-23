# -*- coding: utf-8 -*-

"""
Контроллер для работы с расходами
"""

from models.expense_model import ExpenseModel
from datetime import datetime, timedelta


class ExpenseController:
    """Контроллер для управления расходами"""
    
    def __init__(self, view):
        self.model = ExpenseModel()
        self.view = view
        self.current_date_from = None
        self.current_date_to = None
        self.current_shop_filter = "Все"
    
    def load_data(self, date_from=None, date_to=None, shop=None):
        """Загрузить данные в представление"""
        self.current_date_from = date_from
        self.current_date_to = date_to
        if shop:
            self.current_shop_filter = shop
        
        # Получаем данные из модели
        records = self.model.get_all(date_from, date_to, self.current_shop_filter)
        
        # Обновляем таблицу в представлении
        self.view.display_records(records)
        
        # Обновляем итоги
        self.update_totals()
        
        return records
    
    def add_record(self, data):
        """Добавить новую запись"""
        try:
            record_id = self.model.add(data)
            self.load_data(self.current_date_from, self.current_date_to, self.current_shop_filter)
            return record_id
        except Exception as e:
            print(f"Ошибка при добавлении расхода: {e}")
            return None
    
    def update_record(self, record_id, data):
        """Обновить существующую запись"""
        try:
            self.model.update(record_id, data)
            self.load_data(self.current_date_from, self.current_date_to, self.current_shop_filter)
            return True
        except Exception as e:
            print(f"Ошибка при обновлении расхода: {e}")
            return False
    
    def delete_record(self, record_id):
        """Удалить запись"""
        try:
            self.model.delete(record_id)
            self.load_data(self.current_date_from, self.current_date_to, self.current_shop_filter)
            return True
        except Exception as e:
            print(f"Ошибка при удалении расхода: {e}")
            return False
    
    def process_cell_edit(self, record_id, column, value):
        """Обработка редактирования отдельной ячейки"""
        try:
            # Преобразуем значение для колонки amount
            if column == 'amount':
                try:
                    value = float(value) if value else 0
                except ValueError:
                    value = 0
            
            # Обновляем только одну колонку
            self.model.update(record_id, {column: value})
            
            # Перезагружаем данные
            self.load_data(self.current_date_from, self.current_date_to, self.current_shop_filter)
            return True
        except Exception as e:
            print(f"Ошибка при редактировании ячейки: {e}")
            return False
    
    def set_shop_filter(self, shop):
        """Установить фильтр по магазину"""
        self.current_shop_filter = shop
        self.load_data(self.current_date_from, self.current_date_to, shop)
    
    def update_totals(self):
        """Обновить отображение итогов"""
        total_sum = self.model.get_total_sum(
            self.current_date_from, 
            self.current_date_to,
            self.current_shop_filter if self.current_shop_filter != "Все" else None
        )
        self.view.update_totals(total_sum)
    
    def get_date_range(self, filter_type):
        """Получить диапазон дат для фильтра"""
        today = datetime.now().date()
        
        if filter_type == 'today':
            date_from = today.strftime("%Y-%m-%d")
            date_to = today.strftime("%Y-%m-%d")
        elif filter_type == 'week':
            start_of_week = today - timedelta(days=today.weekday())
            date_from = start_of_week.strftime("%Y-%m-%d")
            date_to = today.strftime("%Y-%m-%d")
        elif filter_type == 'month':
            start_of_month = today.replace(day=1)
            date_from = start_of_month.strftime("%Y-%m-%d")
            date_to = today.strftime("%Y-%m-%d")
        else:
            return None, None
        
        return date_from, date_to
