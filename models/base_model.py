# -*- coding: utf-8 -*-

"""
Базовый класс для работы с базой данных
"""

import sqlite3
from config import DB_PATH, DB_DATE_FORMAT
from datetime import datetime, timedelta


class BaseModel:
    """Базовый класс модели с общими методами для работы с БД"""
    
    def __init__(self, table_name):
        self.table_name = table_name
        self._create_table()
    
    def _get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        """Выполнить запрос и вернуть результат"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if commit:
                conn.commit()
                result = cursor.lastrowid
            elif fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None
                
            return result
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            if commit:
                conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _create_table(self):
        """Создание таблицы (должен быть переопределен)"""
        raise NotImplementedError
    
    def add(self, data):
        """Добавление записи"""
        placeholders = ', '.join(['?' for _ in data])
        columns = ', '.join(data.keys())
        values = list(data.values())
        
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        return self._execute_query(query, values, commit=True)
    
    def update(self, id, data):
        """Обновление записи"""
        set_clause = ', '.join([f"{key}=?" for key in data.keys()])
        values = list(data.values()) + [id]
        
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id=?"
        self._execute_query(query, values, commit=True)
    
    def delete(self, id):
        """Удаление записи"""
        query = f"DELETE FROM {self.table_name} WHERE id=?"
        self._execute_query(query, (id,), commit=True)
    
    def get_by_id(self, id):
        """Получить запись по ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id=?"
        return self._execute_query(query, (id,), fetchone=True)
    
    @staticmethod
    def parse_date(date_str):
        """Преобразование строки в объект date"""
        try:
            return datetime.strptime(date_str, "%d.%m.%Y").date()
        except:
            return None
    
    @staticmethod
    def format_date_for_db(date_str):
        """Преобразование даты из формата отображения в формат БД"""
        if not date_str:
            return datetime.now().strftime(DB_DATE_FORMAT)
        
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            return date_obj.strftime(DB_DATE_FORMAT)
        except:
            return datetime.now().strftime(DB_DATE_FORMAT)
    
    @staticmethod
    def format_date_for_display(date_str):
        """Преобразование даты из формата БД в формат отображения"""
        if not date_str:
            return datetime.now().strftime("%d.%m.%Y")
        
        try:
            date_obj = datetime.strptime(date_str, DB_DATE_FORMAT)
            return date_obj.strftime("%d.%m.%Y")
        except:
            return date_str
