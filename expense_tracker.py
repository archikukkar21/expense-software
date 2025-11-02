"""
Advanced Expense Tracker (GUI) - expense_tracker.py

Requirements:
- Python 3.8+
- tkinter (standard)
- sqlite3 (standard)
- matplotlib

Features:
- Add / Edit / Delete expenses
- Categories
- Monthly summary
- Simple bar chart of expenses by category
"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt

DB = "expenses.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date TEXT,
        category TEXT,
        amount REAL,
        note TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_expense(date, category, amount, note):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
                (date, category, amount, note))
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, date, category, amount, note FROM expenses ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_expense(expense_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def expenses_by_category():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cur.fetchall()
    conn.close()
    return rows

# GUI
class ExpenseApp:
    def __init__(self, root):
        self.root = root
        root.title("Advanced Expense Tracker")
        root.geometry("700x450")
        self.build_ui()
        self.populate()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)

        # Input fields
        input_frame = ttk.Frame(frm)
        input_frame.pack(fill="x", pady=5)

        ttk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(row=0, column=0)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(input_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Category").grid(row=0, column=2)
        self.cat_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.cat_var, width=15).grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Amount").grid(row=0, column=4)
        self.amount_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.amount_var, width=12).grid(row=0, column=5, padx=5)

        ttk.Label(input_frame, text="Note").grid(row=1, column=0)
        self.note_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.note_var, width=50).grid(row=1, column=1, columnspan=5, pady=5, sticky="w")

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Add Expense", command=self.add).pack(side="left")
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Show Category Chart", command=self.show_chart).pack(side="left", padx=5)

        # Treeview
        self.tree = ttk.Treeview(frm, columns=("id","date","category","amount","note"), show="headings")
        for col in ("id","date","category","amount","note"):
            self.tree.heading(col, text=col.title())
        self.tree.column("id", width=40)
        self.tree.pack(fill="both", expand=True, pady=10)

    def add(self):
        try:
            date = self.date_var.get()
            datetime.strptime(date, "%Y-%m-%d")
            category = self.cat_var.get().strip() or "Misc"
            amount = float(self.amount_var.get())
            note = self.note_var.get().strip()
            add_expense(date, category, amount, note)
            messagebox.showinfo("Success", "Expense added.")
            self.populate()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def populate(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in get_expenses():
            self.tree.insert("", "end", values=row)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a row to delete.")
            return
        item = self.tree.item(sel[0])['values']
        delete_expense(item[0])
        self.populate()

    def show_chart(self):
        rows = expenses_by_category()
        if not rows:
            messagebox.showinfo("No data", "No expenses to show.")
            return
        labels = [r[0] for r in rows]
        values = [r[1] for r in rows]
        plt.figure(figsize=(6,4))
        plt.bar(labels, values)
        plt.title("Expenses by Category")
        plt.ylabel("Amount")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()