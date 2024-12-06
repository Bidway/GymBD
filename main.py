import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re

class FitnessApp:
    def __init__(self, master, connection_params):

        self.validation_rules = {
            "numeric_fields": ["id", "возраст", "стоимость", "длительность_дней", "вместимость", "опыт_лет"],
            "text_fields": ["имя"],
        }

        self.master = master
        self.connection_params = connection_params
        self.master.title("Фитнес БД")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        self.conn = sqlite3.connect(**connection_params)
        self.cursor = self.conn.cursor()


        self.table_names = self.get_table_names()

        for table_name in self.table_names:
            frame = tk.Frame(self.notebook)
            self.notebook.add(frame, text=table_name)
            self.create_table_view(frame, table_name)

    def get_table_names(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def create_table_view(self, frame, table_name):
        columns = self.get_columns(table_name)

        tree = self.setup_treeview(frame, columns)
        self.populate_treeview(tree, table_name)

        buttons_frame = tk.Frame(frame)
        buttons_frame.pack(side=tk.TOP, pady=10)

        self.create_button(buttons_frame, "Добавить", lambda: self.add_row(tree, table_name))
        self.create_button(buttons_frame, "Изменить", lambda: self.edit_row(tree, table_name))
        self.create_button(buttons_frame, "Удалить", lambda: self.delete_row(tree, table_name))
        self.create_button(buttons_frame, "Создать отчет", lambda: self.generate_table_report(table_name))

        self.create_search_section(frame, tree, table_name, columns)

    def setup_treeview(self, frame, columns):
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        tree.pack(expand=True, fill="both")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        return tree

    def populate_treeview(self, tree, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name};")
        data = self.cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert("", "end", values=row)

    def create_button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command)
        button.pack(side=tk.LEFT, padx=5)

    def generate_table_report(self, table_name):
        """
        Создает текстовый отчет с информацией из выбранной таблицы.
        Для таблицы "Тренировки" заменяет id на детализированную информацию.
        """
        try:
            report_filename = f"{table_name}_report.txt"
            with open(report_filename, "w", encoding="utf-8") as report_file:
                if table_name == "Тренировки":
                    # Подробный вывод для таблицы "Тренировки"
                    self.cursor.execute('''
                        SELECT 
                            t.id, 
                            cl.имя AS Клиент, 
                            ab.название AS Абонемент, 
                            ha.размер AS Зал, 
                            tr.имя AS Тренер
                        FROM Тренировки t
                        LEFT JOIN Клиенты cl ON t.Клиент_id = cl.id
                        LEFT JOIN Абонементы ab ON t.Абонемент_id = ab.id
                        LEFT JOIN Залы ha ON t.Зал_id = ha.id
                        LEFT JOIN Тренеры tr ON t.Тренер_id = tr.id;
                    ''')
                    rows = self.cursor.fetchall()
                    report_file.write("Отчет по тренировкам:\n")
                    for row in rows:
                        report_file.write(
                            f"ID: {row[0]}, Клиент: {row[1]}, Абонемент: {row[2]}, Зал: {row[3]}, Тренер: {row[4]}\n")
                else:
                    # Вывод для всех остальных таблиц
                    self.cursor.execute(f"SELECT * FROM {table_name};")
                    rows = self.cursor.fetchall()
                    columns = self.get_columns(table_name)
                    report_file.write(f"Отчет по таблице {table_name}:\n")
                    report_file.write("\t".join(columns) + "\n")
                    for row in rows:
                        report_file.write("\t".join(map(str, row)) + "\n")

            messagebox.showinfo("Успех", f"Отчет для таблицы '{table_name}' создан: {report_filename}")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка создания отчета: {e}")
    def create_search_section(self, frame, tree, table_name, columns):
        search_frame = tk.Frame(frame)
        search_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)

        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(search_frame, text="В поле:").pack(side=tk.LEFT, padx=5)
        column_combobox = ttk.Combobox(search_frame, values=columns, state="readonly")
        column_combobox.pack(side=tk.LEFT, padx=5)
        column_combobox.current(0)

        # Кнопка "Найти"
        search_button = tk.Button(
            search_frame,
            text="Найти",
            command=lambda: self.search(tree, search_entry.get(), column_combobox.get(), table_name),
        )
        search_button.pack(side=tk.LEFT, padx=5)

        show_all_button = tk.Button(
            search_frame,
            text="Показать все",
            command=lambda: self.populate_treeview(tree, table_name),
        )
        show_all_button.pack(side=tk.LEFT, padx=5)

    def get_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        return [row[1] for row in self.cursor.fetchall()]

    def open_row_dialog(self, title, columns, defaults=None, save_callback=None):
        dialog = tk.Toplevel(self.master)
        dialog.title(title)

        entry_widgets = {}
        for i, col in enumerate(columns):
            tk.Label(dialog, text=col).grid(row=i, column=0, padx=10, pady=5)
            entry_widgets[col] = self.create_entry_widget(dialog, col, defaults[i] if defaults else None, i)

        submit_button = tk.Button(dialog, text="Сохранить", command=lambda: save_callback(dialog, entry_widgets))
        submit_button.grid(row=len(columns), columnspan=2, pady=10)

    def create_entry_widget(self, parent, col, value, row):
        widget = None
        if col == "название":
            widget = ttk.Combobox(parent, values=["Базовый", "Стандартный", "Премиум", "VIP", "Тренировочный"])
        elif col == "телефон":
            widget = tk.Entry(parent)
        elif col == "специализация":
            widget = ttk.Combobox(parent, values=['Кардиотренировки', 'Силовые тренировки', 'Функциональные тренировки', 'Йога', 'Пилатес'])
        elif col == "размер":
            widget = ttk.Combobox(parent, values=['Большой', 'Средний', 'Малый'])
        elif col == "состояние":
            widget = ttk.Combobox(parent, values=['Хорошее', 'Нормальное', 'Терпимое', 'Ужасное'])
        elif col.endswith("_id"):
            ref_table = col.replace("_id", "")
            options = self.fetch_foreign_key_options(ref_table + "ы")
            widget = ttk.Combobox(parent, values=options)
        else:
            widget = tk.Entry(parent)

        widget.grid(row=row, column=1, padx=10, pady=5)
        if value:
            widget.insert(0, value)
        return widget

    def validate_phone(self, phone_value):
        if re.match(r"^\+375\d{9}$", phone_value):
            return True
        else:
            messagebox.showerror("Ошибка", "Номер телефона должен начинаться с '+375' и содержать 12 цифр.")
            return False

    def validate_numeric(self, value):
        if value.isdigit():
            return True
        else:
            messagebox.showerror("Ошибка", "Значение должно быть числом.")
            return False

    def validate_text(self, value):
        if value.isalpha():
            return True
        else:
            messagebox.showerror("Ошибка", "Значение должно быть текстом, без чисел.")
            return False

    def validate_date(self, new_value):
        if re.match(r"^\d{4}-\d{2}-\d{2}$", new_value) or new_value == "":
            return True
        else:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return False

    def validate_input(self, field_name, value):
        if field_name in self.validation_rules["numeric_fields"]:
            return self.validate_numeric(value)
        elif field_name in self.validation_rules["text_fields"]:
            return self.validate_text(value)
        return True

    def fetch_foreign_key_options(self, ref_table):
        self.cursor.execute(f"SELECT id FROM {ref_table};")
        return [str(row[0]) for row in self.cursor.fetchall()]

    def add_row(self, tree, table_name):
        columns = self.get_columns(table_name)
        self.open_row_dialog(
            f"Добавить строку в {table_name}",
            columns,
            save_callback=lambda dialog, widgets: self.save_new_row(dialog, widgets, tree, table_name),
        )

    def save_new_row(self, dialog, widgets, tree, table_name):
        for col, widget in widgets.items():
            value = widget.get()

            if col == "телефон":
                value = self.ensure_plus_before_save(value)
                widget.delete(0, tk.END)
                widget.insert(0, value)

            if not self.validate_input(col, value):
                return

        values = [widget.get() for widget in widgets.values()]
        placeholders = ", ".join(["?" for _ in values])
        query = f"INSERT INTO {table_name} VALUES ({placeholders});"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.populate_treeview(tree, table_name)
            messagebox.showinfo("Успех", "Запись добавлена!")
            dialog.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {e}")

    def edit_row(self, tree, table_name):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите строку для редактирования.")
            return

        values = tree.item(selected_item)["values"]
        columns = self.get_columns(table_name)
        self.open_row_dialog(
            f"Редактировать строку в {table_name}",
            columns,
            defaults=values,
            save_callback=lambda dialog, widgets: self.save_updated_row(dialog, widgets, tree, table_name, values[0]),
        )

    def save_updated_row(self, dialog, widgets, tree, table_name, row_id):
        # Проверка данных перед сохранением
        for col, widget in widgets.items():
            value = widget.get()

            if col == "телефон":
                value = self.ensure_plus_before_save(value)
                widget.delete(0, tk.END)
                widget.insert(0, value)

            if not self.validate_input(col, value):
                return

        updated_values = [widget.get() for widget in widgets.values()]
        set_clause = ", ".join([f"{col} = ?" for col in widgets.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?;"

        try:
            self.cursor.execute(query, updated_values + [row_id])
            self.conn.commit()
            self.populate_treeview(tree, table_name)
            messagebox.showinfo("Успех", "Запись обновлена!")
            dialog.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить запись: {e}")

    def ensure_plus_before_save(self, value):
        if not value.startswith("+"):
            return "+" + value
        return value
    def delete_row(self, tree, table_name):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите строку для удаления.")
            return

        row_id = tree.item(selected_item)["values"][0]
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
            self.conn.commit()
            self.populate_treeview(tree, table_name)
            messagebox.showinfo("Успех", "Запись удалена!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись: {e}")

    def search(self, tree, query, column, table_name):
        if not query or not column:
            messagebox.showwarning("Предупреждение", "Введите запрос и выберите поле для поиска.")
            return

        try:
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE {column} LIKE ?", (f"%{query}%",))
            data = self.cursor.fetchall()
            tree.delete(*tree.get_children())
            for row in data:
                tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {e}")


if __name__ == "__main__":
    connection_params = {"database": "fitness_db.sqlite3"}
    root = tk.Tk()
    app = FitnessApp(root, connection_params)
    root.mainloop()
