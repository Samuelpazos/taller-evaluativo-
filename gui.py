import tkinter as tk
from tkinter import messagebox
from central_service import Central

class App:
    def __init__(self, root):
        self.c = Central()
        self.root = root
        root.title("Central de Ascensores")
        self.clock = tk.IntVar(value=0)
        self.code = tk.StringVar()
        self.elevator = tk.StringVar()
        self.kind = tk.StringVar(value="EMERGENCY")
        self.step = tk.StringVar()
        self.reverse = tk.StringVar()
        self.reason = tk.StringVar()
        self.build()

    def build(self):
        f = tk.Frame(self.root)
        f.pack(padx=10, pady=10)
        fields = [
            ("Hora", self.clock), ("Código llamada", self.code),
            ("Elevador", self.elevator), ("Paso", self.step),
            ("Reversa", self.reverse), ("Motivo", self.reason)
        ]
        for i, (t, v) in enumerate(fields):
            tk.Label(f, text=t).grid(row=i, column=0, sticky="w")
            tk.Entry(f, textvariable=v, width=30).grid(row=i, column=1)
        tk.Label(f, text="Tipo").grid(row=2, column=2)
        tk.OptionMenu(f, self.kind, "EMERGENCY", "MAINTENANCE").grid(row=2, column=3)
        buttons = [
            ("Registrar", self.register), ("Atender", self.attend),
            ("Ejecutar paso", self.execute), ("Deshacer", self.undo),
            ("Abortar", self.abort), ("Cerrar", self.close), ("Reporte", self.report)
        ]
        for i, (t, cmd) in enumerate(buttons):
            tk.Button(f, text=t, command=cmd, width=15).grid(row=i, column=4, padx=5, pady=2)
        self.listbox = tk.Listbox(self.root, width=80, height=12)
        self.listbox.pack(padx=10, pady=10)
        self.current = None

    def register(self):
        msg = self.c.register(self.code.get(), self.elevator.get(), self.kind.get(), self.clock.get())
        messagebox.showinfo("Resultado", msg)
        self.refresh()

    def attend(self):
        self.current = self.c.attend(self.clock.get())
        messagebox.showinfo("Resultado", "Llamada atendida" if self.current else "No hay llamadas")
        self.refresh()

    def execute(self):
        if not self.current:
            messagebox.showinfo("Resultado", "No hay llamada activa")
            return
        msg = self.c.execute(self.current, self.step.get(), self.reverse.get())
        messagebox.showinfo("Resultado", msg)
        self.refresh()

    def undo(self):
        if not self.current:
            messagebox.showinfo("Resultado", "No hay llamada activa")
            return
        messagebox.showinfo("Resultado", self.c.undo(self.current))
        self.refresh()

    def abort(self):
        if not self.current:
            messagebox.showinfo("Resultado", "No hay llamada activa")
            return
        messagebox.showinfo("Resultado", self.c.abort(self.current, self.reason.get()))
        self.refresh()

    def close(self):
        if not self.current:
            messagebox.showinfo("Resultado", "No hay llamada activa")
            return
        messagebox.showinfo("Resultado", self.c.close(self.current, self.clock.get()))
        self.refresh()

    def report(self):
        messagebox.showinfo("Reporte", self.c.report())

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for e in self.c.park:
            self.listbox.insert(tk.END, f"{e.code} | {e.location} | {e.state} | emergencias={e.emergencies}")
        self.listbox.insert(tk.END, f"Emergencias en cola: {len(self.c.emergency)}")
        self.listbox.insert(tk.END, f"Mantenimientos en cola: {len(self.c.maintenance)}")
