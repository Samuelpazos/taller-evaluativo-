import tkinter as tk
from tkinter import ttk, messagebox
from services.lab_service import LabService

class EquipmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Engineering Laboratory Equipment")
        self.root.geometry("1366x768")
        self.service = LabService()
        self.build()

    def build(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Load Sample Data", command=self.load).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="left", padx=5)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=5)
        self.inventory_tab()
        self.loan_tab()
        self.carts_tab()
        self.review_tab()

    def inventory_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text="Inventory")
        form = ttk.Frame(tab); form.pack(fill="x")
        self.code = tk.StringVar(); self.kind = tk.StringVar(value="PORTATIL")
        ttk.Entry(form, textvariable=self.code, width=15).pack(side="left")
        ttk.Combobox(form, textvariable=self.kind, values=["PORTATIL","KIT","MULTIMETRO"], state="readonly", width=15).pack(side="left", padx=5)
        ttk.Button(form, text="Add", command=self.add).pack(side="left")
        ttk.Button(form, text="Remove", command=self.remove).pack(side="left", padx=5)
        self.search_code = tk.StringVar()
        ttk.Entry(form, textvariable=self.search_code, width=15).pack(side="left", padx=(25,5))
        ttk.Button(form, text="Search", command=self.search).pack(side="left")
        cols = ("Code","Type","Status","Loans","Cart Position")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings")
        for c in cols: self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, pady=8)

    def loan_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text="Loan Counter")
        f = ttk.Frame(tab); f.pack(fill="x")
        self.student = tk.StringVar(); self.loan_kind = tk.StringVar(value="PORTATIL"); self.hour = tk.StringVar(value="0"); self.return_code = tk.StringVar()
        for var, label in [(self.student,"Student"),(self.hour,"Hour"),(self.return_code,"Return code")]:
            ttk.Label(f,text=label).pack(side="left"); ttk.Entry(f,textvariable=var,width=12).pack(side="left",padx=4)
        ttk.Combobox(f,textvariable=self.loan_kind,values=["PORTATIL","KIT","MULTIMETRO"],state="readonly",width=13).pack(side="left",padx=4)
        ttk.Button(f,text="Request",command=self.request).pack(side="left")
        ttk.Button(f,text="Return",command=self.return_eq).pack(side="left",padx=4)
        self.queues = tk.Text(tab, height=15)
        self.queues.pack(fill="both", expand=True, pady=8)

    def carts_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text="Carts")
        self.carts_text = tk.Text(tab)
        self.carts_text.pack(fill="both", expand=True)

    def review_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text="Review & Reports")
        f = ttk.Frame(tab); f.pack(fill="x")
        ttk.Button(f,text="Approve Next",command=lambda:self.review(False)).pack(side="left")
        ttk.Button(f,text="Report Damage",command=lambda:self.review(True)).pack(side="left",padx=5)
        self.report_text = tk.Text(tab, height=15); self.report_text.pack(fill="both",expand=True)
        self.log_text = tk.Text(tab, height=8); self.log_text.pack(fill="both",expand=True)

    def result(self, ok, msg):
        (messagebox.showinfo if ok else messagebox.showerror)("Result", msg)
        self.service.log.append(msg)
        self.refresh()

    def load(self):
        self.service.load_sample(); self.refresh()

    def add(self):
        ok,msg=self.service.add_equipment(self.code.get(),self.kind.get()); self.result(ok,msg)

    def remove(self):
        ok,msg=self.service.remove_equipment(self.code.get()); self.result(ok,msg)

    def search(self):
        r=self.service.search(self.search_code.get())
        if not r: return self.result(False,"Equipment not found")
        e,p=r; self.result(True,f"{e.code} | {e.status} | cart position from top: {p}")

    def request(self):
        try: hour=int(self.hour.get())
        except: return self.result(False,"Hour must be an integer")
        ok,msg=self.service.request(self.student.get(),self.loan_kind.get(),hour); self.result(ok,msg)

    def return_eq(self):
        try: hour=int(self.hour.get())
        except: return self.result(False,"Hour must be an integer")
        ok,msg=self.service.return_equipment(self.return_code.get(),hour); self.result(ok,msg)

    def review(self, damaged):
        ok,msg=self.service.review_next(damaged); self.result(ok,msg)

    def refresh(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        for e in self.service.inventory.values():
            p=self.service.search(e.code)[1]
            self.tree.insert("","end",values=(e.code,e.kind,e.status,e.loans,p or "-"))
        self.queues.delete("1.0","end")
        for k,q in self.service.waiting.items():
            self.queues.insert("end",f"{k} | FRONT -> {q.values()} <- REAR\n")
        self.queues.insert("end",f"REVIEW | FRONT -> {[x[0].code for x in self.service.review.values()]} <- REAR\n")
        self.queues.insert("end",f"STORAGE | FRONT -> {[x.code for x in self.service.to_store.values()]} <- REAR\n")
        self.carts_text.delete("1.0","end")
        for k,s in self.service.carts.items():
            self.carts_text.insert("end",f"{k} CART | TOP -> {s.values()} | {len(s)}/{self.service.capacity}\n")
        r=self.service.report()
        self.report_text.delete("1.0","end"); self.report_text.insert("end",str(r))
        self.log_text.delete("1.0","end"); self.log_text.insert("end","\n".join(self.service.log[-30:]))

if __name__ == "__main__":
    root=tk.Tk(); EquipmentApp(root); root.mainloop()
