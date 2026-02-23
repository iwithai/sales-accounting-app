# -*- coding: utf-8 -*-

"""
Главное окно приложения с вкладками
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import SHOPS
from views.sales_view import SalesView
from views.expense_view import ExpenseView
from controllers.sales_controller import SalesController
from controllers.expense_controller import ExpenseController


class MainView:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        
        # Создаем контроллеры
        self.sales_controllers = {}
        self.expense_controller = ExpenseController(None)
        
        # Создаем интерфейс
        self._create_menu()
        self._create_notebook()
        self._create_global_summary()
        
        # Загружаем начальные данные
        self._load_initial_data()
    
    def _create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт в Excel", command=self._export_to_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
    
    def _create_notebook(self):
        """Создание вкладок"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаем вкладки для магазинов
        self.shop_views = {}
        for shop in SHOPS:
            # Создаем контроллер для магазина
            controller = SalesController(shop, None)
            self.sales_controllers[shop] = controller
            
            # Создаем представление
            view = SalesView(self.notebook, shop, controller)
            self.notebook.add(view, text=shop)
            
            # Устанавливаем связь контроллер-представление
            controller.view = view
            self.shop_views[shop] = view
        
        # Создаем вкладку расходов
        self.expense_view = ExpenseView(self.notebook, self.expense_controller)
        self.notebook.add(self.expense_view, text="Расходы")
        
        # Устанавливаем связь контроллер-представление для расходов
        self.expense_controller.view = self.expense_view
        
        # Привязываем событие переключения вкладок для обновления итогов
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
    
    def _create_global_summary(self):
        """Создание общей панели итогов внизу окна"""
        summary_frame = ttk.LabelFrame(self.root, text="Общие итоги за выбранную дату")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Создаем фрейм для итогов
        totals_frame = ttk.Frame(summary_frame)
        totals_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Магазин 1
        self.shop1_total_label = ttk.Label(totals_frame, text=f"{SHOPS[0]}: 0.00 сом.", font=('Arial', 10, 'bold'))
        self.shop1_total_label.pack(side=tk.LEFT, padx=10)
        
        # Магазин 2
        self.shop2_total_label = ttk.Label(totals_frame, text=f"{SHOPS[1]}: 0.00 сом.", font=('Arial', 10, 'bold'))
        self.shop2_total_label.pack(side=tk.LEFT, padx=10)
        
        # Всего продажи
        ttk.Label(totals_frame, text="Всего:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(20, 5))
        self.total_sales_label = ttk.Label(totals_frame, text="0.00 сом.", font=('Arial', 10, 'bold'))
        self.total_sales_label.pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        ttk.Label(totals_frame, text="|", font=('Arial', 12)).pack(side=tk.LEFT, padx=10)
        
        # Расходы
        ttk.Label(totals_frame, text="Расходы:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.expense_total_label = ttk.Label(totals_frame, text="0.00 руб.", font=('Arial', 10, 'bold'))
        self.expense_total_label.pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        ttk.Label(totals_frame, text="|", font=('Arial', 12)).pack(side=tk.LEFT, padx=10)
        
        # ИТОГО
        ttk.Label(totals_frame, text="ИТОГО:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.grand_total_label = ttk.Label(totals_frame, text="0.00 сом.", font=('Arial', 10, 'bold'))
        self.grand_total_label.pack(side=tk.LEFT, padx=5)
    
    def _on_tab_changed(self, event):
        """Обработка переключения вкладки - обновляем общие итоги"""
        self._update_global_totals()
    
    def _update_global_totals(self):
        """Обновление общих итогов"""
        # Получаем суммы из каждой вкладки
        shop1_total = self.shop_views[SHOPS[0]].get_total_sales()
        shop2_total = self.shop_views[SHOPS[1]].get_total_sales()
        total_sales = shop1_total + shop2_total
        expense_total = self.expense_view.get_total_expense()
        grand_total = total_sales - expense_total
        
        # Обновляем метки
        self.shop1_total_label.config(text=f"{SHOPS[0]}: {shop1_total:.2f} сом.")
        self.shop2_total_label.config(text=f"{SHOPS[1]}: {shop2_total:.2f} сом.")
        self.total_sales_label.config(text=f"{total_sales:.2f} сом.")
        self.expense_total_label.config(text=f"{expense_total:.2f} сом.")
        self.grand_total_label.config(text=f"{grand_total:.2f} сом.")
    
    def _load_initial_data(self):
        """Загрузка начальных данных"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Загружаем данные за сегодня для всех магазинов
        for shop, controller in self.sales_controllers.items():
            controller.load_data(today, today)
        
        # Загружаем расходы за сегодня
        self.expense_controller.load_data(today, today)
        
        # Обновляем общие итоги
        self._update_global_totals()
    
    def _export_to_excel(self):
        """Экспорт данных в Excel"""
        messagebox.showinfo("Экспорт", "Функция экспорта будет доступна в следующей версии")
    
    def _show_about(self):
        """Показать информацию о программе"""
        about_text = """Учет продаж и расходов
Версия 1.0

Программа для учета продаж двух магазинов и расходов.

Возможности:
- Учет продаж по магазинам
- Учет расходов
- Фильтрация по дате
- Редактирование через окно
- Автодополнение товаров

© 2024"""
        
        messagebox.showinfo("О программе", about_text)
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            self.root.quit()
