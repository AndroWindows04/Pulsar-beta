import customtkinter as ctk
import database as db
from tkinter import messagebox

class PulsarAdminPromoter(ctk.CTkToplevel):
    def __init__(self, group_name, parent_app):
        super().__init__()
        self.group_name = group_name
        self.app = parent_app
        self.title("Назначение администратора")
        self.geometry("350x200")
        self.attributes("-topmost", True)
        
        ctk.CTkLabel(self, text=f"👑 Новый админ в: {group_name}", font=("Arial", 14, "bold")).pack(pady=10)
        
        g = db.load_db()["groups"].get(group_name, {})
        all_m = list(set(g.get("members", []) + g.get("subscribers", [])))
        if self.app.current_user in all_m: 
            all_m.remove(self.app.current_user)
        
        self.var = ctk.StringVar(value=all_m if all_m else "")
        ctk.CTkOptionMenu(self, values=all_m, variable=self.var).pack(pady=10)
        
        ctk.CTkButton(self, text="Назначить админом", fg_color="#34C759", command=self.exec_promote).pack(pady=15)

    def exec_promote(self):
        user = self.var.get()
        if not user: 
            return
        db.manage_member(self.group_name, user, "promote")
        messagebox.showinfo("Успех", f"Пользователь @{user} теперь администратор!")
        self.destroy()
