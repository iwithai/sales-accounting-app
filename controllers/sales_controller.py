# -*- coding: utf-8 -*-

"""
Контроллер для работы с продажами
"""

from models.sale_model import SaleModel
from datetime import datetime, timedelta


class SalesController:
    """Контроллер для управления продажами одного магазина"""
    
    def __init__(self, shop_name, view):
        self.shop_name = shop_name
        self.model = SaleModel(shop_name)
        self.view = view
        self.current_date_from = None
        self.current_date_to = None
    
    def load_data(self, date_from=None, date_to=None):
        """Загрузить данные в представление"""
        self.current_date_from = date_from
        self.current_date_to = date_to
        
        # Получаем данные из модели
        records = self.model.get_all(date_from, date_to)
        
        # Фильтруем записи только для текущего магазина
        shop_records = [r for r in records if r.get('shop') == self.shop_name]
        
        # Обновляем таблицу в представлении
        self.view.display_records(shop_records)
        
        # Обновляем итоги
        self.update_totals()
        
        return shop_records
    
    def add_record(self, data):
        """Добавить новую запись"""
        try:
            record_id = self.model.add(data)
            self.load_data(self.current_date_from, self.current_date_to)
            return record_id
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            return None
    
    def update_record(self, record_id, data):
        """Обновить существующую запись"""
        try:
            self.model.update(record_id, data)
            self.load_data(self.current_date_from, self.current_date_to)
            return True
        except Exception as e:
            print(f"Ошибка при обновлении записи: {e}")
            return False
    
    def delete_record(self, record_id):
        """Удалить запись"""
        try:
            self.model.delete(record_id)
            self.load_data(self.current_date_from, self.current_date_to)
            return True
        except Exception as e:
            print(f"Ошибка при удалении записи: {e}")
            return False
    
    def update_totals(self):
        """Обновить отображение итогов"""
        total_sum = self.model.get_total_sum(
            self.current_date_from, 
            self.current_date_to
        )
        self.view.update_totals(total_sum)
    
    def get_date_range(self, filter_type):
        """Получить диапазон дат для фильтра"""
        today = datetime.now().date()
        
        if filter_type == 'today':
            date_from = today.strftime("%Y-%m-%d")
            date_to = today.strftime("%Y-%m-%d")
        elif filter_type == 'week':
            # Начало недели (понедельник)
            start_of_week = today - timedelta(days=today.weekday())
            date_from = start_of_week.strftime("%Y-%m-%d")
            date_to = today.strftime("%Y-%m-%d")
        elif filter_type == 'month':
            # Начало месяца
            start_of_month = today.replace(day=1)
            date_from = start_of_month.strftime("%Y-%m-%d")
            date_to = today.strftime("%Y-%m-%d")
        else:
            return None, None
        
        return date_from, date_to
