import sqlite3
import tkinter as tk
from tkinter import messagebox

DB_NAME = "employees.db"
FIELDS = [
    ("full_name",  "ФИО"),
    ("position",   "Должность"),
    ("department", "Отдел"),
    ("hire_date",  "Дата приёма"),
    ("salary",     "Оклад"),
]


class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сервер")
        self.root.geometry("520x360")
        self.root.resizable(False, False)

        # --- состояние ---
        self.records = []          # список кортежей записей
        self.index = 0             # текущая позиция
        self.bookmark = None       # индекс закладки или None

        # --- подключение к БД ---
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()
        self._load_records()

        # --- интерфейс ---
        self._build_ui()
        self._refresh()

    # ---------- данные ----------
    def _load_records(self):
        self.cur.execute("""
            SELECT full_name, position, department, hire_date, salary
            FROM employees
            ORDER BY id
        """)
        self.records = self.cur.fetchall()

    # ---------- интерфейс ----------
    def _build_ui(self):
        # Поля записи
        frame_fields = tk.LabelFrame(self.root, text="Текущая запись", padx=10, pady=10)
        frame_fields.pack(fill="x", padx=10, pady=(10, 5))

        self.field_vars = {}
        for row, (key, label) in enumerate(FIELDS):
            tk.Label(frame_fields, text=label + ":", anchor="w", width=14)\
                .grid(row=row, column=0, sticky="w", pady=2)
            var = tk.StringVar()
            tk.Label(frame_fields, textvariable=var, anchor="w", relief="sunken",
                     bg="white", width=40).grid(row=row, column=1, sticky="we", pady=2)
            self.field_vars[key] = var
        frame_fields.columnconfigure(1, weight=1)

        # Индикатор позиции
        self.pos_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.pos_var, font=("Arial", 11, "bold"))\
            .pack(pady=(5, 5))

        # Панель навигации
        frame_nav = tk.LabelFrame(self.root, text="Навигация", padx=10, pady=8)
        frame_nav.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_nav, text="<< Первая",  width=12,
                  command=self.go_first).pack(side="left", padx=4)
        tk.Button(frame_nav, text="< Предыдущая", width=12,
                  command=self.go_prev).pack(side="left", padx=4)
        tk.Button(frame_nav, text="Следующая >", width=12,
                  command=self.go_next).pack(side="left", padx=4)
        tk.Button(frame_nav, text="Последняя >>", width=12,
                  command=self.go_last).pack(side="left", padx=4)

        # Панель «Закладка»
        frame_bm = tk.LabelFrame(self.root, text="Закладка", padx=10, pady=8)
        frame_bm.pack(fill="x", padx=10, pady=(5, 10))

        tk.Button(frame_bm, text="Установить закладку", width=22,
                  command=self.set_bookmark).pack(side="left", padx=4)
        tk.Button(frame_bm, text="Перейти к закладке", width=22,
                  command=self.goto_bookmark).pack(side="left", padx=4)

        self.bookmark_var = tk.StringVar()
        tk.Label(frame_bm, textvariable=self.bookmark_var, anchor="w", fg="navy")\
            .pack(side="left", padx=10)

    # ---------- обновление отображения ----------
    def _refresh(self):
        if not self.records:
            for var in self.field_vars.values():
                var.set("")
            self.pos_var.set("Запись 0 из 0")
            return

        rec = self.records[self.index]
        for (key, _), value in zip(FIELDS, rec):
            if key == "salary":
                self.field_vars[key].set(f"{value:,.2f} руб.".replace(",", " "))
            else:
                self.field_vars[key].set(str(value))

        self.pos_var.set(f"Запись {self.index + 1} из {len(self.records)}")

        if self.bookmark is None:
            self.bookmark_var.set("Закладка не установлена")
        else:
            name = self.records[self.bookmark][0]
            self.bookmark_var.set(f"Закладка: запись {self.bookmark + 1} ({name})")

    # ---------- навигация ----------
    def go_first(self):
        if self.records and self.index != 0:
            self.index = 0
            self._refresh()

    def go_prev(self):
        if self.records and self.index > 0:
            self.index -= 1
            self._refresh()

    def go_next(self):
        if self.records and self.index < len(self.records) - 1:
            self.index += 1
            self._refresh()

    def go_last(self):
        if self.records and self.index != len(self.records) - 1:
            self.index = len(self.records) - 1
            self._refresh()

    # ---------- закладка ----------
    def set_bookmark(self):
        if not self.records:
            return
        self.bookmark = self.index
        self._refresh()

    def goto_bookmark(self):
        if self.bookmark is None:
            messagebox.showinfo("Закладка", "Закладка не установлена.")
            return
        self.index = self.bookmark
        self._refresh()

    # ---------- завершение ----------
    def on_close(self):
        self.conn.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()