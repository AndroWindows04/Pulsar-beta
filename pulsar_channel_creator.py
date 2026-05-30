import customtkinter as ctk
import database as db
from tkinter import messagebox

class PulsarChannelCreator(ctk.CTkToplevel):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.title("Создание объекта Pulsar")
        self.geometry("350x400")
        self.attributes("-topmost", True)
        
        ctk.CTkLabel(self, text="🛠️ Создать группу или канал", font=("Arial", 16, "bold")).pack(pady=15)
        
        ctk.CTkLabel(self, text="Название:").pack()
        self.name_entry = ctk.CTkEntry(self, width=250, placeholder_text="Например: Новости Технологий")
        self.name_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Тип объекта:").pack(pady=(10,5))
        self.type_var = ctk.StringVar(value="group")
        ctk.CTkRadioButton(self, text="👥 Группа (Все пишут)", variable=self.type_var, value="group").pack()
        ctk.CTkRadioButton(self, text="📢 Канал (Только админы)", variable=self.type_var, value="channel").pack(pady=5)
        
        ctk.CTkButton(self, text="✨ Создать", fg_color="#34C759", command=self.create_object).pack(pady=30)

    def create_object(self):
        title = self.name_entry.get().strip()
        g_type = self.type_var.get()
        
        if not title:
            messagebox.showerror("Ошибка", "Введите название!")
            return
            
        data = db.load_db()
        if title in data["groups"] or title in data["history"]:
            messagebox.showerror("Ошибка", "Такое название уже занято!")
            return
            
        data["groups"][title] = {
            "owner": self.app.current_user,
            "admins": [],
            "members": [self.app.current_user] if g_type == "group" else [],
            "subscribers": [self.app.current_user] if g_type == "channel" else [],
            "banned": [],
            "type": g_type,
            "avatar": ""
        }
        data["history"][title] = []
        
        db.save_db(data)
        messagebox.showinfo("Успех", f"{'Группа' if g_type == 'group' else 'Канал'} '{title}' успешно создана!")
        
        self.app.render_chats_list()
        self.destroy()
