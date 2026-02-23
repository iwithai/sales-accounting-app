# -*- coding: utf-8 -*-

"""
Виджет для выбора даты из трех списков: год, месяц, день
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, date


class DateSelector(ttk.Frame):
    """Виджет для выбора даты из трех выпадающих списков"""
    
    def __init__(self, master, initial_date=None, on_change=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.on_change = on_change
        self.current_date = None
        
        # Текущая дата для определения диапазонов
        today = datetime.now()
        current_year = today.year
        current_month = today.month
        current_day = today.day
        
        # Создаем списки значений
        self.years = list(range(current_year - 4, current_year + 5))
        self.months = list(range(1, 13))
        self.days = list(range(1, 32))
        
        # Переменные для хранения выбранных значений
        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.day_var = tk.StringVar()
        
        # Создаем выпадающие списки
        self.year_combo = ttk.Combobox(
            self,
            textvariable=self.year_var,
            values=self.years,
            state="readonly",
            width=6
        )
        self.year_combo.pack(side=tk.LEFT, padx=1)
        self.year_combo.bind('<<ComboboxSelected>>', self._on_change)
        
        self.month_combo = ttk.Combobox(
            self,
            textvariable=self.month_var,
            values=self.months,
            state="readonly",
            width=4
        )
        self.month_combo.pack(side=tk.LEFT, padx=1)
        self.month_combo.bind('<<ComboboxSelected>>', self._on_month_change)
        
        self.day_combo = ttk.Combobox(
            self,
            textvariable=self.day_var,
            values=self.days,
            state="readonly",
            width=4
        )
        self.day_combo.pack(side=tk.LEFT, padx=1)
        self.day_combo.bind('<<ComboboxSelected>>', self._on_change)
        
        # Устанавливаем начальную дату
        if initial_date:
            self.set_date(initial_date)
        else:
            self.set_date(today)
    
    def _on_month_change(self, event=None):
        """Обработка изменения месяца - обновляем дни"""
        self._update_days()
        self._on_change()
    
    def _update_days(self):
        """Обновление количества дней в зависимости от месяца и года"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            
            # Определяем количество дней в месяце
            if month in [1, 3, 5, 7, 8, 10, 12]:
                max_days = 31
            elif month in [4, 6, 9, 11]:
                max_days = 30
            else:  # февраль
                # Проверка на високосный год
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    max_days = 29
                else:
                    max_days = 28
            
            # Обновляем список дней
            self.days = list(range(1, max_days + 1))
            self.day_combo['values'] = self.days
            
            # Корректируем текущий день, если он выходит за пределы
            current_day = self.day_var.get()
            if current_day and int(current_day) > max_days:
                self.day_var.set(str(max_days))
        
        except (ValueError, TypeError):
            pass
    
    def _on_change(self, event=None):
        """Обработка изменения даты"""
        if self.on_change:
            self.on_change()
    
    def get_date(self):
        """Получить выбранную дату в формате строки"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            
            # Проверяем корректность даты
            date_obj = date(year, month, day)
            return date_obj.strftime("%d.%m.%Y")
        except (ValueError, TypeError):
            return None
    
    def get_date_obj(self):
        """Получить объект date"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            return date(year, month, day)
        except (ValueError, TypeError):
            return None
    
    def set_date(self, date_value):
        """Установить дату"""
        if isinstance(date_value, (datetime, date)):
            year = date_value.year
            month = date_value.month
            day = date_value.day
        elif isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, "%d.%m.%Y")
                year = date_obj.year
                month = date_obj.month
                day = date_obj.day
            except:
                today = datetime.now()
                year = today.year
                month = today.month
                day = today.day
        else:
            today = datetime.now()
            year = today.year
            month = today.month
            day = today.day
        
        # Убеждаемся, что год есть в списке
        if year not in self.years:
            # Добавляем год в список и сортируем
            self.years.append(year)
            self.years.sort()
            self.year_combo['values'] = self.years
        
        self.year_var.set(str(year))
        self.month_var.set(str(month))
        
        # Обновляем дни для нового месяца
        self._update_days()
        
        # Устанавливаем день
        self.day_var.set(str(day))
