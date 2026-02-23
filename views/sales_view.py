# -*- coding: utf-8 -*-

"""
Представление для вкладки продаж
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import SALES_COLUMNS, TABLE_FONT, HEADER_FONT, COLORS
from views.widgets.date_selector import DateSelector
from datetime import datetime


class SalesView(ttk.Frame):
    """Представление для отображения и редактирования продаж"""
    
    def __init__(self, master, shop_name, controller):
        super().__init__(master)
        
        self.shop_name = shop_name
        self.controller = controller
        self.records = []  # Текущие записи
        self.selected_record_id = None  # ID выбранной записи
        self.selected_row_widgets = []  # Виджеты выбранной строки
        self.total_sales = 0  # Сумма продаж
        
        self._create_widgets()
        self._bind_events()
        
        # Настраиваем веса для прокрутки при изменении размера
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной контейнер
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель с фильтром по дате
        filter_frame = ttk.Frame(main_container)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Дата:").pack(side=tk.LEFT, padx=5)
        
        self.filter_date = DateSelector(filter_frame, on_change=self._apply_date_filter)
        self.filter_date.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            filter_frame,
            text="Сегодня",
            command=self._set_today_filter
        ).pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        ttk.Separator(main_container, orient='horizontal').pack(fill=tk.X, padx=5, pady=5)
        
        # Панель для добавления новой записи
        add_frame = ttk.LabelFrame(main_container, text="Добавить запись")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Поля для ввода в одну строку
        fields_frame = ttk.Frame(add_frame)
        fields_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Продавец
        ttk.Label(fields_frame, text="Продавец:").pack(side=tk.LEFT, padx=2)
        self.seller_entry = ttk.Entry(fields_frame, width=12)
        self.seller_entry.pack(side=tk.LEFT, padx=2)
        self.seller_entry.bind('<Return>', self._add_record_event)
        
        # Товар (простое поле, без автодополнения)
        ttk.Label(fields_frame, text="Товар:").pack(side=tk.LEFT, padx=2)
        self.item_entry = ttk.Entry(fields_frame, width=15)
        self.item_entry.pack(side=tk.LEFT, padx=2)
        self.item_entry.bind('<Return>', self._add_record_event)
        
        # Количество
        ttk.Label(fields_frame, text="Кол-во:").pack(side=tk.LEFT, padx=2)
        self.quantity_entry = ttk.Entry(fields_frame, width=6)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(side=tk.LEFT, padx=2)
        self.quantity_entry.bind('<Return>', self._add_record_event)
        
        # Цена
        ttk.Label(fields_frame, text="Цена:").pack(side=tk.LEFT, padx=2)
        self.price_entry = ttk.Entry(fields_frame, width=8)
        self.price_entry.pack(side=tk.LEFT, padx=2)
        self.price_entry.bind('<Return>', self._add_record_event)
        
        # Кнопка добавления
        self.add_button = ttk.Button(
            fields_frame,
            text="Добавить",
            command=self._add_record
        )
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        ttk.Separator(main_container, orient='horizontal').pack(fill=tk.X, padx=5, pady=5)
        
        # Таблица с прокруткой
        table_container = ttk.Frame(main_container)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаем Canvas и Scrollbar для прокрутки
        self.canvas = tk.Canvas(table_container, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self._on_canvas_scroll)
        h_scrollbar = ttk.Scrollbar(main_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        # Фрейм для таблицы внутри Canvas
        self.table_frame = ttk.Frame(self.canvas)
        self.table_frame.bind("<Configure>", self._on_frame_configure)
        
        # Создаем окно в Canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        
        # Настраиваем Canvas
        self.canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Привязываем событие изменения размера Canvas
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Размещаем Canvas и Scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Создаем заголовки таблицы
        self._create_headers()
        
        # Панель с итогами только для этой вкладки
        summary_frame = ttk.Frame(main_container)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.total_label = ttk.Label(summary_frame, text=f"Итого {self.shop_name}: 0.00 сом", font=HEADER_FONT)
        self.total_label.pack(side=tk.LEFT, padx=5)
    
    def _on_canvas_configure(self, event):
        """Обработка изменения размера Canvas"""
        # Обновляем ширину окна таблицы
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_frame_configure(self, event):
        """Обработка изменения размера фрейма таблицы"""
        # Обновляем область прокрутки Canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_scroll(self, *args):
        """Обработка прокрутки Canvas"""
        self.canvas.yview(*args)
    
    def _create_headers(self):
        """Создание заголовков таблицы"""
        columns = list(SALES_COLUMNS.keys()) + ['actions']
        
        for col_index, col in enumerate(columns):
            if col == 'actions':
                text = 'Действия'
                width = 150 // 7
            else:
                text = SALES_COLUMNS[col]['text']
                width = SALES_COLUMNS[col]['width'] // 7
            
            header = tk.Label(
                self.table_frame,
                text=text,
                bg=COLORS['header_bg'],
                font=HEADER_FONT,
                relief=tk.RIDGE,
                width=width
            )
            header.grid(row=0, column=col_index, sticky='nsew')
    
    def _bind_events(self):
        """Привязка событий"""
        self.bind('<Delete>', self._on_delete)
    
    def _set_today_filter(self):
        """Установить сегодняшнюю дату в фильтр"""
        self.filter_date.set_date(datetime.now())
        self._apply_date_filter()
    
    def _apply_date_filter(self):
        """Применить фильтр по дате"""
        selected_date = self.filter_date.get_date_obj()
        if selected_date:
            date_str = selected_date.strftime("%Y-%m-%d")
            self.controller.load_data(date_str, date_str)
    
    def _add_record_event(self, event=None):
        """Обработка нажатия Enter для добавления записи"""
        self._add_record()
    
    def _add_record(self):
        """Добавить новую запись"""
        # Берем дату из фильтра
        filter_date = self.filter_date.get_date()
        if not filter_date:
            messagebox.showerror("Ошибка", "Выберите дату в фильтре")
            return
        
        data = {
            'date': filter_date,
            'seller_name': self.seller_entry.get(),
            'item': self.item_entry.get(),
            'quantity': self.quantity_entry.get(),
            'price': self.price_entry.get()
        }
        
        if not data['item']:
            messagebox.showerror("Ошибка", "Поле 'Товар' обязательно для заполнения")
            return
        
        if not data['quantity']:
            data['quantity'] = '1'
        
        if not data['price']:
            data['price'] = '0'
        
        self.controller.add_record(data)
        
        # Очищаем поля
        self.seller_entry.delete(0, tk.END)
        self.item_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")
        self.price_entry.delete(0, tk.END)
        
        # Фокус на поле Продавец
        self.seller_entry.focus()
        
        self.after(100, self._scroll_to_bottom)
    
    def display_records(self, records):
        """Отображение записей в таблице"""
        for widget in self.table_frame.winfo_children():
            if int(widget.grid_info().get('row', 0)) > 0:
                widget.destroy()
        
        self.records = records
        sorted_records = sorted(records, key=lambda x: x.get('date', ''))
        
        # Считаем общую сумму продаж
        self.total_sales = sum(float(r.get('total', 0)) for r in records)
        
        for i, record in enumerate(sorted_records):
            row = i + 1
            columns = list(SALES_COLUMNS.keys()) + ['actions']
            
            for col_index, col in enumerate(columns):
                if col == 'actions':
                    # Создаем фрейм с кнопками
                    actions_frame = ttk.Frame(self.table_frame)
                    actions_frame.grid(row=row, column=col_index, sticky='nsew', padx=1, pady=1)
                    
                    edit_btn = ttk.Button(
                        actions_frame,
                        text="✎",
                        width=3,
                        command=lambda r=record['id']: self._edit_record(r)
                    )
                    edit_btn.pack(side=tk.LEFT, padx=1)
                    
                    delete_btn = ttk.Button(
                        actions_frame,
                        text="✕",
                        width=3,
                        command=lambda r=record['id']: self._delete_record(r)
                    )
                    delete_btn.pack(side=tk.LEFT, padx=1)
                    
                    # Привязываем клик по фрейму для выбора строки
                    actions_frame.bind('<Button-1>', lambda e, r=record['id'], row_idx=row: self._on_row_click(e, r, row_idx))
                    edit_btn.bind('<Button-1>', lambda e, r=record['id']: self._on_row_click(e, r, row))
                    delete_btn.bind('<Button-1>', lambda e, r=record['id']: self._on_row_click(e, r, row))
                    
                else:
                    value = record.get(col, '')
                    
                    if col in ['quantity', 'price', 'total']:
                        try:
                            value = f"{float(value):.2f}"
                        except:
                            pass
                    
                    cell = tk.Label(
                        self.table_frame,
                        text=str(value),
                        bg=COLORS['table_bg'] if i % 2 == 0 else COLORS['table_alternate'],
                        font=TABLE_FONT,
                        relief=tk.RIDGE,
                        anchor='e' if col in ['quantity', 'price', 'total'] else 'w'
                    )
                    cell.grid(row=row, column=col_index, sticky='nsew')
                    
                    cell.bind('<Button-1>', lambda e, r=record['id'], row_idx=row: self._on_row_click(e, r, row_idx))
            
            # Настраиваем веса колонок
            for col_index in range(len(columns)):
                self.table_frame.columnconfigure(col_index, weight=1)
        
        # Обновляем итог
        self.update_totals(self.total_sales)
        
        if records:
            self.after(100, self._scroll_to_bottom)
    
    def update_totals(self, total_sum):
        """Обновление отображения итогов"""
        self.total_sales = total_sum
        self.total_label.config(text=f"Итого {self.shop_name}: {total_sum:.2f} сом")
    
    def get_total_sales(self):
        """Получить общую сумму продаж"""
        return self.total_sales
    
    def _on_row_click(self, event, record_id, row):
        """Обработка клика по строке"""
        self.selected_record_id = record_id
        
        # Снимаем выделение с предыдущей строки
        for widget in self.selected_row_widgets:
            try:
                if isinstance(widget, tk.Label):
                    if widget.grid_info().get('row', 0) % 2 == 0:
                        widget.config(bg=COLORS['table_bg'])
                    else:
                        widget.config(bg=COLORS['table_alternate'])
            except:
                pass
        
        self.selected_row_widgets = []
        
        # Подсвечиваем новую строку
        for widget in self.table_frame.winfo_children():
            if hasattr(widget, 'grid_info'):
                info = widget.grid_info()
                if info.get('row') == row and isinstance(widget, tk.Label):
                    widget.config(bg=COLORS['select'])
                    self.selected_row_widgets.append(widget)
    
    def _edit_record(self, record_id):
        """Редактировать запись"""
        self._start_row_edit(record_id)
    
    def _delete_record(self, record_id):
        """Удалить запись"""
        if messagebox.askyesno("Подтверждение", f"Удалить запись?"):
            self.controller.delete_record(record_id)
            self.selected_record_id = None
            self.selected_row_widgets = []
    
    def _start_row_edit(self, record_id):
        """Начать редактирование всей строки"""
        record = None
        for r in self.records:
            if r['id'] == record_id:
                record = r
                break
        
        if not record:
            return
        
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Редактирование записи")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        
        fields = [
            ('Дата', 'date', record.get('date', '')),
            ('Продавец', 'seller_name', record.get('seller_name', '')),
            ('Товар', 'item', record.get('item', '')),
            ('Количество', 'quantity', record.get('quantity', '')),
            ('Цена', 'price', record.get('price', ''))
        ]
        
        entries = {}
        for i, (label, field, value) in enumerate(fields):
            ttk.Label(edit_window, text=label + ":").grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            if field == 'date':
                entry = DateSelector(edit_window)
                entry.set_date(value)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            else:
                entry = ttk.Entry(edit_window, width=25)
                entry.insert(0, str(value))
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
                entry.bind('<Return>', lambda e, f=field: self._save_edit_on_enter(e, edit_window, record_id, entries))
            
            entries[field] = entry
        
        btn_frame = ttk.Frame(edit_window)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        def save():
            data = {}
            for field, entry in entries.items():
                if field == 'date':
                    data[field] = entry.get_date()
                else:
                    data[field] = entry.get()
            
            self.controller.update_record(record_id, data)
            edit_window.destroy()
        
        ttk.Button(btn_frame, text="Сохранить", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
        
        edit_window.bind('<Return>', lambda e: save())
        edit_window.bind('<Escape>', lambda e: edit_window.destroy())
    
    def _save_edit_on_enter(self, event, edit_window, record_id, entries):
        """Сохранить при нажатии Enter в поле редактирования"""
        data = {}
        for field, entry in entries.items():
            if field == 'date':
                data[field] = entry.get_date()
            else:
                data[field] = entry.get()
        
        self.controller.update_record(record_id, data)
        edit_window.destroy()
    
    def _on_delete(self, event):
        """Обработка нажатия Delete"""
        if self.selected_record_id:
            self._delete_record(self.selected_record_id)
    
    def _scroll_to_bottom(self):
        """Прокрутить таблицу к последней записи"""
        if hasattr(self, 'canvas'):
            self.canvas.yview_moveto(1.0)
