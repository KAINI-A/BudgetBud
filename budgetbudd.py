import json
import math
from datetime import datetime
# Decimal is better than float for handling money
from decimal import Decimal, InvalidOperation
# Makes working with file paths easier
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# File where all the data will be stored
DATA_FILE = Path("records.json")
CATEGORIES = ["Food", "Rent", "Entertainment", "Transport",
              "Utilities", "Savings", "Other"]


def now_string():
    """Return current date-time as MM/DD/YYYY HH:MM."""
    return datetime.now().strftime("%m/%d/%Y %H:%M")


def to_decimal(text):
    """Convert string to Decimal"""
    try:
        return Decimal(text)
    except InvalidOperation:
        raise ValueError("Amount must be a number.")


# DATA CLASS
class Transaction:
    """One income or expense line."""

    def __init__(self, date, desc, amount, kind, category):
        self.date = date
        self.description = desc
        self.amount = amount          # Decimal
        self.kind = kind              # "Income" or "Expense"
        self.category = category      # chosen from CATEGORIES

    def to_json(self):
        return {
            "date": self.date,"description": self.description,"amount": str(self.amount),"kind": self.kind,"category": self.category
        }

    @staticmethod
    def from_json(d):
        return Transaction(d["date"], d["description"],Decimal(str(d["amount"])),d["kind"], d.get("category", "Other"))

class Goal:
    """Savings goal with name and target amount."""

    def __init__(self, name, target):
        self.name = name
        self.target = target       

    def to_json(self):
        return {"name": self.name, "target": str(self.target)}

    @staticmethod
    def from_json(d):
        return Goal(d["name"], Decimal(str(d["target"])))


class DataManager:
    """ Handles all saving/loading of data """

    def __init__(self, path=DATA_FILE):
        self.path = path
        self.transactions = []   # list of Transaction
        self.goals = []          # list of Goal
        self.load()  

    # Totals and balances
    def income_total(self):
        return sum(t.amount for t in self.transactions if t.kind == "Income")

    def expense_total(self):
        return sum(t.amount for t in self.transactions if t.kind == "Expense")

    def balance(self):
        return self.income_total() - self.expense_total()

    def savings_total(self):
        return max(Decimal(0), self.balance())

    # Calculates total expenses for each category.   
    def category_totals(self):
        # Initializes all categories with 0, then loops through all transactions. 
        totals = {c: Decimal(0) for c in CATEGORIES}
        for t in self.transactions:
            if t.kind == "Expense":
                totals[t.category] += t.amount
        return totals

    # Functions to add/update/delete things
    def add_transaction(self, t):
        self.transactions.append(t)
        self.save()

    def update_transaction(self, index, t):
        self.transactions[index] = t
        self.save()

    def delete_transaction(self, index):
        self.transactions.pop(index)
        self.save()

    def add_goal(self, g):
        self.goals.append(g)
        self.save()

    def update_goal(self, index, g):
        self.goals[index] = g
        self.save()

    def delete_goal(self, index):
        self.goals.pop(index)
        self.save()

    # Save/load the data to/from jsonfile
    def load(self):
        """Load data from the JSON file (if it exists)."""
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text())
        except json.JSONDecodeError:
            messagebox.showwarning("Warning", "Could not read data file.")
            return

        # Compatibility with old format (just in case)
        if isinstance(data, list):
            data = {"transactions": data, "goals": []}

        self.transactions = [Transaction.from_json(d) for d in data.get("transactions", [])]
        self.goals = [Goal.from_json(d) for d in data.get("goals", [])]

    def save(self):
        obj = {"transactions": [t.to_json() for t in self.transactions],"goals": [g.to_json() for g in self.goals],}
        self.path.write_text(json.dumps(obj, indent=2))

# GUI
# It builds all the tabs and keeps everything organized
class BudgetBuddy(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)

        # Creates data manager which handles all the loading/saving
        self.dm = DataManager()

        #Window features
        self.pack(fill="both", expand=True)
        root.title("Budget Buddy")
        root.geometry("800x560")

        #Tab builder
        self.build_tabs()
        self.build_transactions_tab()
        self.build_goals_tab()
        self.build_categories_tab()
        self.build_dashboard_tab()

        self.refresh_all()

    #TABS LAYOUT
    def build_tabs(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        #frame for each tab
        self.tab_txn = ttk.Frame(self.nb)
        self.tab_goal = ttk.Frame(self.nb)
        self.tab_cat = ttk.Frame(self.nb)
        self.tab_dash = ttk.Frame(self.nb)

        #labels
        self.nb.add(self.tab_txn, text="Transactions")
        self.nb.add(self.tab_goal, text="Goals")
        self.nb.add(self.tab_cat, text="Categories")
        self.nb.add(self.tab_dash, text="Dashboard")

    # Transactions tab
    def build_transactions_tab(self):

        #create form to add new txn
        form = ttk.LabelFrame(self.tab_txn, text="New transaction")
        form.pack(fill="x", padx=10, pady=8)

        #user input
        self.var_date = tk.StringVar(value=now_string())
        self.var_desc = tk.StringVar()
        self.var_amt = tk.StringVar()
        self.var_kind = tk.StringVar(value="Expense")
        self.var_cat = tk.StringVar(value=CATEGORIES[0])

        ttk.Label(form, text="Date").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_date).grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_desc).grid(row=1, column=1, sticky="ew")

        ttk.Label(form, text="Amount").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_amt).grid(row=2, column=1, sticky="ew")

        #Buttons for income and expense
        ttk.Label(form, text="Type").grid(row=0, column=2)
        fr_kind = ttk.Frame(form)
        fr_kind.grid(row=0, column=3, rowspan=2, sticky="w")
        ttk.Radiobutton(fr_kind, text="Income", variable=self.var_kind,
                        value="Income").pack(side="left")
        ttk.Radiobutton(fr_kind, text="Expense", variable=self.var_kind,
                        value="Expense").pack(side="left")

        #Dropdown for category
        ttk.Label(form, text="Category").grid(row=2, column=2, sticky="w")
        ttk.Combobox(form, values=CATEGORIES, textvariable=self.var_cat,
                     state="readonly").grid(row=2, column=3, sticky="w")

        #Add delete buttons
        ttk.Button(form, text="Add", command=self.add_transaction) \
            .grid(row=0, column=4, rowspan=2, padx=5)
        ttk.Button(form, text="Delete selected", command=self.delete_transaction) \
            .grid(row=2, column=4, padx=5)

        # stretch first two columns
        for col in (1,):
            form.columnconfigure(col, weight=1)

        #Table for list of txns
        cols = ("date", "desc", "amount", "kind", "cat")
        self.tree_txn = ttk.Treeview(self.tab_txn, columns=cols,show="headings", selectmode="browse")
        self.tree_txn.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        #Header and column size
        widths = (150, 260, 90, 80, 90)
        for c, w in zip(cols, widths):
            self.tree_txn.heading(c, text=c.title())
            self.tree_txn.column(c, width=w, anchor="center" if c != "desc" else "w")

        #keyboard and mouse events
        self.tree_txn.bind("<Delete>", lambda e: self.delete_transaction())
        self.tree_txn.bind("<Double-1>", self.edit_transaction)

    #GOALS TAB
    def build_goals_tab(self):
        #buttons
        bar = ttk.Frame(self.tab_goal)
        bar.pack(fill="x", padx=10, pady=8)
        ttk.Button(bar, text="Add goal", command=self.add_goal).pack(side="left")
        ttk.Button(bar, text="Edit selected", command=self.edit_goal) \
            .pack(side="left", padx=4)
        ttk.Button(bar, text="Delete selected", command=self.delete_goal) \
            .pack(side="left")

        #Table for list of goals
        cols = ("name", "target", "progress")
        self.tree_goal = ttk.Treeview(self.tab_goal, columns=cols, show="headings", selectmode="browse")
        self.tree_goal.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        #Header and column size
        self.tree_goal.heading("name", text="Name")
        self.tree_goal.heading("target", text="Target")
        self.tree_goal.heading("progress", text="Progress")

        self.tree_goal.column("name", width=220)
        self.tree_goal.column("target", width=100, anchor="e")
        self.tree_goal.column("progress", width=340)

        #Mouse action
        self.tree_goal.bind("<Double-1>", self.edit_goal)

    #CATEGORIES TAB
    def build_categories_tab(self):
        #Table showing categories and total amnt
        self.tree_cat = ttk.Treeview(self.tab_cat, columns=("cat", "amt"), show="headings")
        self.tree_cat.heading("cat", text="Category")
        self.tree_cat.heading("amt", text="Amount")
        self.tree_cat.column("cat", width=160)
        self.tree_cat.column("amt", width=120, anchor="e")
        self.tree_cat.pack(side="right", fill="y", padx=6, pady=8)

        #Pie chart frame
        self.cat_chart_frame = ttk.Frame(self.tab_cat)
        self.cat_chart_frame.pack(fill="both", expand=True, padx=10, pady=8)
        #Placeholder
        self.cat_chart_canvas = None

    #DASHBOARD TAB

    def build_dashboard_tab(self):
        self.lbl_balance = ttk.Label(self.tab_dash, font=("Arial", 20, "bold"))
        self.lbl_balance.pack(pady=10)

        #Bar chart
        self.dash_chart_frame = ttk.Frame(self.tab_dash)
        self.dash_chart_frame.pack(fill="both", expand=True, padx=10, pady=8)
        #Placeholder
        self.dash_canvas = None

    # TXNS ACTIONS
    # Fxn triggered when the user clicks "Add"
    def add_transaction(self):
        """Validate form and add to list."""
        try:
            #ip from the input
            t = Transaction(self.var_date.get(),
                self.var_desc.get(),
                to_decimal(self.var_amt.get()),
                self.var_kind.get(),
                self.var_cat.get()
            )
            # date check
            datetime.strptime(t.date, "%m/%d/%Y %H:%M")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        #Add to data manager and clear the form
        self.dm.add_transaction(t)
        self.var_date.set(now_string())
        self.var_desc.set("")
        self.var_amt.set("")
        self.refresh_all()

    #Delets selected txns from table and data
    def delete_transaction(self):
        sel = self.tree_txn.focus()
        #if nothing is selected
        if not sel:
            return

        #using first tag to store the index
        idx = int(self.tree_txn.item(sel, "tags")[0])
        if messagebox.askyesno("Delete", "Delete selected transaction?"):
            self.dm.delete_transaction(idx)
            #refreshes the table
            self.refresh_all()

    # Opens a small popup window to edit a selected transactio
    def edit_transaction(self, _event=None):
        sel = self.tree_txn.focus()
        if not sel:
            return
        idx = int(self.tree_txn.item(sel, "tags")[0])
        t = self.dm.transactions[idx]

        #new window
        dlg = tk.Toplevel(self)
        dlg.title("Edit transaction")
        dlg.grab_set()

        #fill the form with current txns values
        v_date = tk.StringVar(value=t.date)
        v_desc = tk.StringVar(value=t.description)
        v_amt = tk.StringVar(value=str(t.amount))
        v_kind = tk.StringVar(value=t.kind)
        v_cat = tk.StringVar(value=t.category)

        # Create widgets 
        ttk.Label(dlg, text="Date").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(dlg, textvariable=v_date).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(dlg, text="Description").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(dlg, textvariable=v_desc).grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(dlg, text="Amount").grid(row=2, column=0, sticky="w", padx=5)
        ttk.Entry(dlg, textvariable=v_amt).grid(row=2, column=1, sticky="ew", padx=5)

        ttk.Label(dlg, text="Type").grid(row=0, column=2)
        fr_kind = ttk.Frame(dlg)
        fr_kind.grid(row=0, column=3, rowspan=2, sticky="w")

        #Create buttons
        ttk.Radiobutton(fr_kind, text="Income", variable=v_kind,
                        value="Income").pack(side="left")
        ttk.Radiobutton(fr_kind, text="Expense", variable=v_kind,
                        value="Expense").pack(side="left")

        ttk.Label(dlg, text="Category").grid(row=2, column=2)
        ttk.Combobox(dlg, values=CATEGORIES, textvariable=v_cat,
                     state="readonly").grid(row=2, column=3)

        #Save changes when save button is clicked
        def save_edit():
            try:
                new_t = Transaction(
                    v_date.get(), v_desc.get(),
                    to_decimal(v_amt.get()), v_kind.get(), v_cat.get())
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)
                return
            self.dm.update_transaction(idx, new_t)
            dlg.destroy()
            self.refresh_all()

        ttk.Button(dlg, text="Save", command=save_edit) \
            .grid(row=3, column=0, columnspan=4, pady=6)
        dlg.columnconfigure(1, weight=1)
        dlg.resizable(False, False)

    #GOAL ACTIONS
    #New popup to add new goal
    def add_goal(self):
        self.goal_dialog()

    #opens popup to edit goal
    def edit_goal(self, _event=None):
        sel = self.tree_goal.focus()
        if sel:
            idx = int(self.tree_goal.item(sel, "tags")[0])
            self.goal_dialog(idx)

    #deletes goal 
    def delete_goal(self):
        sel = self.tree_goal.focus()
        if not sel:
            return
        idx = int(self.tree_goal.item(sel, "tags")[0])
        g = self.dm.goals[idx]
        if messagebox.askyesno("Delete", f'Delete goal "{g.name}"?'):
            self.dm.delete_goal(idx)
            self.refresh_all()

    def goal_dialog(self, idx=None):
        """Open add/edit dialog; idx=None means new."""
        g = self.dm.goals[idx] if idx is not None else None

        #new popup
        dlg = tk.Toplevel(self)
        dlg.title("Goal")
        dlg.grab_set()

        #User ip holder
        v_name = tk.StringVar(value=g.name if g else "")
        v_tgt = tk.StringVar(value=str(g.target) if g else "")

        #Form for goal name and target
        ttk.Label(dlg, text="Name").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(dlg, textvariable=v_name).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(dlg, text="Target").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(dlg, textvariable=v_tgt).grid(row=1, column=1, sticky="ew", padx=5)

        #Save button saves data and closed the popup
        def save_goal():
            try:
                new_g = Goal(v_name.get(), to_decimal(v_tgt.get()))
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)
                return

            if idx is None:
                # ADD a new goal
                self.dm.add_goal(new_g)
            else:
                # UPDATE the existing goal
                self.dm.update_goal(idx, new_g)

            dlg.destroy()
            #prevents popup from being resized
            self.refresh_all()

        ttk.Button(dlg, text="Save", command=save_goal) \
            .grid(row=2, column=0, columnspan=2, pady=6)

        dlg.columnconfigure(1, weight=1)
        dlg.resizable(False, False)

    # Rebuilds the entire transaction table based on current data
    def refresh_transactions_table(self):
        self.tree_txn.delete(*self.tree_txn.get_children())
        for i, t in enumerate(self.dm.transactions):
            self.tree_txn.insert(
                "", "end",
                values=(t.date, t.description, f"{t.amount:,.2f}",
                        t.kind, t.category),
                tags=(str(i),))

    # Rebuilds the goals table and shows a progress bar for each goal
    def refresh_goals_table(self):
        self.tree_goal.delete(*self.tree_goal.get_children())
        bal = self.dm.balance()
        for i, g in enumerate(self.dm.goals):
            pct = min(1, float(bal / g.target) if g.target > 0 else 1)
            bar_len = 20
            filled = math.ceil(pct * bar_len)

            #\u2588 = block char
            bar = "\u2588" * filled + " " * (bar_len - filled)
            progress = f"{bar} {pct * 100:.0f}%"
            self.tree_goal.insert("", "end",values=(g.name, f"{g.target:,.2f}", progress),tags=(str(i),))

    # Updates the pie chart and table showing spending by category
    def refresh_categories_tab(self):
        totals = self.dm.category_totals()
        # * unpacks the list and so each ID is passed as seperate arg to del()
        self.tree_cat.delete(*self.tree_cat.get_children())
        labels = []
        sizes = []
        for cat, amt in totals.items():
            if amt > 0:
                self.tree_cat.insert("", "end",values=(cat, f"{amt:,.2f}"))
                labels.append(cat)
                sizes.append(float(amt))

        # Remove old chart if it exists
        if self.cat_chart_canvas:
            self.cat_chart_canvas.get_tk_widget().destroy()
            self.cat_chart_canvas = None

        #Create and display pie chart
        if sizes:
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels,autopct=lambda p: f"{p:.0f}%",startangle=90)
            ax.set_title("Expenses by Category")
            self.cat_chart_canvas = FigureCanvasTkAgg(fig, master=self.cat_chart_frame)
            self.cat_chart_canvas.draw()
            self.cat_chart_canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

     # Updates the dashboard showing total income, expense, and savings
    def refresh_dashboard(self):
        self.lbl_balance.config(text=f"Current balance: ${self.dm.balance():,.2f}")

        #remove old chart if it exists
        if self.dash_canvas:
            self.dash_canvas.get_tk_widget().destroy()
            self.dash_canvas = None

        #Create bar chart
        fig, ax = plt.subplots()
        ax.bar(["Income", "Expense", "Savings"],[float(self.dm.income_total()),float(self.dm.expense_total()),float(self.dm.savings_total())],color=["green", "red", "blue"])
        ax.set_ylabel("USD")
        ax.bar_label(ax.containers[0], fmt="%.2f", padding=3)

        self.dash_canvas = FigureCanvasTkAgg(fig, master=self.dash_chart_frame)
        self.dash_canvas.draw()
        self.dash_canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # Helper function to refresh everything at once
    def refresh_all(self):
        self.refresh_transactions_table()
        self.refresh_goals_table()
        self.refresh_categories_tab()
        self.refresh_dashboard()


#MAIN FUNCTION :)
if __name__ == "__main__":
    root = tk.Tk()
    BudgetBuddy(root)
    root.mainloop()
