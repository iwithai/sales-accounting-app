#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главный файл запуска приложения учета продаж и расходов
"""

import sys
import os

# Добавляем путь к корневой папке проекта в sys.path
# Это позволит импортировать модули из корня проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.main_view import MainView
import tkinter as tk


def main():
    """Главная функция запуска приложения"""
    root = tk.Tk()
    root.title("Учет продаж и расходов")
    root.geometry("1200x700")
    
    # Устанавливаем иконку (если есть)
    try:
        root.iconbitmap(default="icon.ico")
    except:
        pass
    
    app = MainView(root)
    
    # Обработка закрытия окна
    def on_closing():
        app.on_closing()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()
